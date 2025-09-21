from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import csv
import io

from database import get_db, create_tables
from services.voting_service import VotingService
from config import Config
from auth import AuthService, require_admin, require_voter
from email_service import email_service

# Initialize FastAPI app
app = FastAPI(
    title="SecureVote Pro - Advanced Voting System",
    description="A professional voting system using advanced data structures and cryptography",
    version="2.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize voting service
voting_service = VotingService()

# Pydantic models for request/response
class VoteRequest(BaseModel):
    otac: str
    candidate_id: str

class LoginRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class OTPVerificationRequest(BaseModel):
    email: str
    otp_code: str
    temp_token: str

class ResendOTPRequest(BaseModel):
    email: str
    username: str

class ProofRequest(BaseModel):
    ballot_hash: str

class VerifyProofRequest(BaseModel):
    leaf: str
    leaf_index: int
    proof: list[str]
    root: str

# Initialize database tables on startup
create_tables()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to login page."""
    return HTMLResponse(content='<script>window.location.href="/login";</script>')

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page."""
    with open("templates/login.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve the admin dashboard."""
    with open("templates/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/voter", response_class=HTMLResponse)
async def voter_portal():
    """Serve the voter portal."""
    with open("templates/voter.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Authentication Endpoints

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return JWT token or initiate 2FA for voters."""
    try:
        import re
        # Validate username and password
        if not re.match(r"^[a-zA-Z0-9_]+$", request.username):
            raise HTTPException(status_code=400, detail="Invalid username format")
        if len(request.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        # Verify credentials (simplified - in production use proper password hashing)
        user_role = None
        if request.username == "admin" and request.password == "admin123":
            user_role = "admin"
        elif request.username == "election_commissioner" and request.password == "commissioner123":
            user_role = "admin"  # Same privileges as admin
        elif request.username == "voter" and request.password == "voter123":
            user_role = "voter"
        if not user_role:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if 2FA is required (only for voters)
        if user_role == "voter":
            if not request.email:
                raise HTTPException(status_code=400, detail="Email address is required for voter authentication")
            
            # Send OTP to email
            otp_result = email_service.send_otp_email(request.email, request.username)
            
            if not otp_result["success"]:
                raise HTTPException(status_code=500, detail=otp_result["error"])
            
            # Create temporary token for OTP verification
            temp_token_data = {
                "sub": request.username,
                "role": user_role,
                "email": request.email,
                "temp": True,
                "exp": datetime.utcnow() + timedelta(minutes=10)  # 10 minutes for OTP process
            }
            temp_token = AuthService.create_access_token(temp_token_data)
            
            response_data = {
                "requires_2fa": True,
                "temp_token": temp_token,
                "message": otp_result["message"],
                "expires_in": otp_result["expires_in"]
            }
            
            # Include dev OTP only in development mode
            if Config.DEVELOPMENT_MODE and "dev_otp" in otp_result:
                response_data["dev_otp"] = otp_result["dev_otp"]
            
            return response_data
        
        else:
            # Direct login for admin/commissioner (no 2FA)
            token_data = {
                "sub": request.username,
                "role": user_role,
                "exp": datetime.utcnow() + timedelta(minutes=30)
            }
            access_token = AuthService.create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "role": user_role,
                "username": request.username,
                "requires_2fa": False
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/auth/verify-otp")
async def verify_otp(request: OTPVerificationRequest):
    """Verify OTP and complete voter login."""
    try:
        # Verify the temporary token
        try:
            payload = AuthService.verify_token(request.temp_token)
            if not payload.get("temp"):
                raise HTTPException(status_code=401, detail="Invalid temporary token")
        except:
            raise HTTPException(status_code=401, detail="Invalid or expired temporary token")
        
        # Verify OTP
        otp_result = email_service.verify_otp(request.email, request.otp_code)
        
        if not otp_result["success"]:
            raise HTTPException(status_code=400, detail=otp_result["error"])
        
        # Create final access token
        token_data = {
            "sub": otp_result["username"],
            "role": "voter",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        access_token = AuthService.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "voter",
            "username": otp_result["username"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")

@app.post("/auth/resend-otp")
async def resend_otp(request: ResendOTPRequest):
    """Resend OTP to voter's email."""
    try:
        # Send new OTP
        otp_result = email_service.send_otp_email(request.email, request.username)
        
        if not otp_result["success"]:
            raise HTTPException(status_code=500, detail=otp_result["error"])
        
        response_data = {
            "message": otp_result["message"],
            "expires_in": otp_result["expires_in"]
        }
        
        # Include dev OTP only in development mode
        if Config.DEVELOPMENT_MODE and "dev_otp" in otp_result:
            response_data["dev_otp"] = otp_result["dev_otp"]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend OTP: {str(e)}")

@app.post("/admin/register-voters")
async def admin_register_voters(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Register voters from CSV file."""
    try:
        content = await file.read()
        csv_data = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        voters = []
        for row in csv_reader:
            if 'voter_id' in row and 'name' in row:
                voters.append({
                    'voter_id': row['voter_id'].strip(),
                    'name': row['name'].strip()
                })
        
        if not voters:
            raise HTTPException(status_code=400, detail="No valid voter data found in CSV")
        
        # Extract just the voter_ids for the service
        voter_ids = [voter['voter_id'] for voter in voters]
        
        result = voting_service.register_voters(db, voter_ids)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True, 
            "registered_count": result["registered_count"],
            "duplicate_count": result["duplicate_count"], 
            "total_voters": result["total_voters"],
            "message": f"Registered {result['registered_count']} voters"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.post("/admin/issue-otacs")
async def admin_issue_otacs(request: dict, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Issue OTACs for specified voters."""
    try:
        voter_ids = request.get("voter_ids", [])
        if not voter_ids:
            raise HTTPException(status_code=400, detail="No voter IDs provided")
        
        result = voting_service.issue_otacs(db, voter_ids)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to issue OTACs: {str(e)}")

@app.get("/admin/results")
async def admin_get_results(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Get voting results for admin."""
    try:
        results_data = voting_service.get_results(db)
        return results_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.get("/admin/audit-trail")
async def admin_get_audit_trail(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Get audit trail for admin."""
    try:
        events = voting_service.get_audit_trail(db)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")

@app.get("/admin/ballot-lookup/{ballot_hash}")
async def admin_ballot_lookup(ballot_hash: str, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Lookup ballot details by hash for admin."""
    try:
        result = voting_service.lookup_ballot(db, ballot_hash)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lookup ballot: {str(e)}")

@app.get("/admin/generate-proof/{ballot_hash}")
async def admin_generate_proof(ballot_hash: str, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Generate Merkle proof for admin."""
    try:
        proof = voting_service.generate_merkle_proof(db, ballot_hash)
        if not proof:
            raise HTTPException(status_code=404, detail="Ballot not found")
        return proof
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate proof: {str(e)}")

# Voter Endpoints (Protected)

@app.post("/voter/cast-vote")
async def voter_cast_vote(vote_request: VoteRequest, db: Session = Depends(get_db), current_user: dict = Depends(require_voter)):
    """Cast a vote using OTAC (voter access only)."""
    try:
        result = voting_service.cast_vote(db, vote_request.otac, vote_request.candidate_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cast vote: {str(e)}")

# Legacy endpoints (kept for backward compatibility)

@app.post("/cast-vote")
async def cast_vote(vote_request: VoteRequest, db: Session = Depends(get_db)):
    """Cast a vote using OTAC (legacy endpoint)."""
    try:
        result = voting_service.cast_vote(db, vote_request.otac, vote_request.candidate_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cast vote: {str(e)}")

@app.get("/results")
async def get_results(db: Session = Depends(get_db)):
    """Get current voting results."""
    try:
        return voting_service.get_results(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.get("/generate-proof/{ballot_hash}")
async def generate_proof(ballot_hash: str, db: Session = Depends(get_db)):
    """Generate Merkle proof for a ballot hash."""
    try:
        result = voting_service.generate_merkle_proof(db, ballot_hash)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate proof: {str(e)}")

@app.post("/verify-proof")
async def verify_proof(verify_request: VerifyProofRequest, db: Session = Depends(get_db)):
    """Verify a Merkle proof."""
    try:
        result = voting_service.verify_merkle_proof(
            verify_request.leaf,
            verify_request.leaf_index,
            verify_request.proof,
            verify_request.root
        )
        return {"valid": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify proof: {str(e)}")

@app.post("/api/undoLast")
async def undo_last(db: Session = Depends(get_db)):
    """Undo last action (demo mode only)."""
    try:
        result = voting_service.undo_last_action(db)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to undo action: {str(e)}")

@app.get("/api/auditTrail")
async def get_audit_trail(limit: int = 50, db: Session = Depends(get_db)):
    """Get audit trail."""
    try:
        return {"events": voting_service.get_audit_trail(db, limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    try:
        return voting_service.get_system_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/admin/otp-stats")
async def admin_get_otp_stats(current_user: dict = Depends(require_admin)):
    """Get OTP storage statistics for admin."""
    try:
        from utils.simple_otp_storage import otp_storage
        stats = otp_storage.get_stats()
        return {
            "success": True,
            "otp_storage": stats,
            "cleanup_count": email_service.cleanup_expired_otps()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get OTP stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
