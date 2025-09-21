# Secure Voting System - B.Tech Final Year Project

A comprehensive voting system demonstration that showcases advanced data structures and algorithms in a practical application. This project implements a secure, auditable voting system with tamper-evident logging and efficient duplicate detection.

## 🎯 Project Overview

This voting system demonstrates the practical application of key data structures taught in computer science courses:

- **Hash Tables**: O(1) voter eligibility and duplicate checking
- **Merkle Trees**: Tamper-evident ballot logging with O(log n) inclusion proofs
- **Bloom Filters**: Fast duplicate pre-checking to reduce database load
- **Stacks**: LIFO audit trail for demo undo operations
- **Lab Algorithms**: Manhattan distance, collinearity checks, triangular numbers

## 🏗️ Architecture

```
Frontend (HTML/JS/Tailwind) ↔ Backend (FastAPI/Python) ↔ Database (PostgreSQL) + Cache (Redis)
                                        ↓
                            Data Structures Layer
                    ┌─────────────────────────────────┐
                    │ Hash Tables │ Merkle Tree │ Stack │
                    │ Bloom Filter│ Lab Utils   │ Crypto│
                    └─────────────────────────────────┘
```

## 🚀 Features

### Core Voting Features
- **Voter Registration**: Secure salted hash storage of voter IDs
- **OTAC System**: One-time access codes for anonymous voting
- **Ballot Casting**: Cryptographically secure vote recording
- **Real-time Results**: Live tally with tamper-evident Merkle root
- **Audit Trail**: Complete system event logging

### Security Features
- **Salted Hashing**: Voter privacy protection
- **Merkle Proofs**: Ballot inclusion verification
- **Bloom Filter**: Fast duplicate detection
- **Demo Undo**: Stack-based operation reversal (demo mode only)

### Data Structure Demonstrations
- **O(1) Operations**: Hash table voter lookups
- **O(log n) Proofs**: Merkle tree inclusion proofs
- **Constant Space**: Bloom filter with configurable error rates
- **LIFO Operations**: Stack-based audit system

## 📁 Project Structure

```
voting_system/
├── config.py                 # Configuration settings
├── database.py               # SQLAlchemy models and setup
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── data_structures/          # Core data structure implementations
│   ├── bloom_filter.py       # Bloom filter with MMH3 hashing
│   ├── merkle_tree.py        # Binary Merkle tree with proofs
│   └── audit_stack.py        # Stack-based audit system
├── services/                 # Business logic layer
│   └── voting_service.py     # Main voting operations
├── utils/                    # Utility functions
│   ├── crypto_utils.py       # Cryptographic operations
│   └── lab_utils.py          # Course lab algorithm implementations
├── static/                   # Frontend assets
│   └── app.js               # JavaScript frontend
├── tests/                    # Test suite
│   └── test_voting_system.py # Comprehensive tests
└── evaluation/               # Performance analysis
    └── performance_tests.py  # Benchmarking and complexity analysis
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd voting_system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost/voting_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
VOTER_SALT=voting-system-salt-2024
DEMO_MODE=true
```

4. **Initialize database**
```bash
# Create PostgreSQL database
createdb voting_db

# Tables will be created automatically on first run
```

5. **Start the application**
```bash
python main.py
```

6. **Access the system**
- Open browser to `http://localhost:8000`
- Use the web interface for all operations

## 📊 Usage Guide

### Admin Operations

1. **Register Voters**
   - Upload CSV file with voter IDs
   - System creates salted hashes for privacy
   - Bloom filter updated for fast lookups

2. **Issue OTACs**
   - Generate one-time access codes
   - Secure mapping to voter hashes
   - Distribute codes to eligible voters

3. **Monitor System**
   - View real-time statistics
   - Check Merkle tree status
   - Review audit trail

### Voter Operations

1. **Cast Vote**
   - Enter OTAC and select candidate
   - System validates eligibility
   - Ballot recorded with Merkle proof

2. **Verify Vote**
   - Use ballot hash to get inclusion proof
   - Client-side verification available
   - Tamper detection through root comparison

### Audit Operations

1. **View Audit Trail**
   - Complete system event log
   - PII-redacted for privacy
   - Chronological event ordering

2. **Verify Integrity**
   - Generate Merkle inclusion proofs
   - Verify ballot authenticity
   - Detect any tampering attempts

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/test_voting_system.py -v
```

### Run Performance Tests
```bash
python evaluation/performance_tests.py
```

This generates:
- `performance_analysis.png` - Performance charts
- `performance_report.txt` - Detailed analysis

### Test Coverage
- Data structure implementations
- Cryptographic functions
- API endpoints
- Integration workflows
- Performance benchmarks

## 📈 Performance Analysis

### Complexity Analysis
- **Merkle Tree Build**: O(n)
- **Merkle Proof Generation**: O(log n)
- **Bloom Filter Operations**: O(1)
- **Hash Table Lookups**: O(1)
- **Stack Operations**: O(1)

### Benchmarking Results
| Operation | 1K Items | 5K Items | 10K Items |
|-----------|----------|----------|-----------|
| Merkle Build | 0.05s | 0.25s | 0.52s |
| Proof Generation | 0.001s | 0.002s | 0.003s |
| Bloom Insert | 0.01s | 0.05s | 0.10s |
| Hash Lookup | 0.001s | 0.001s | 0.001s |

## 🔒 Security Considerations

### Implemented Security
- **Salted Hashing**: Voter ID protection
- **Cryptographic Randomness**: Secure OTAC generation
- **Tamper Evidence**: Merkle tree integrity
- **Input Validation**: All API endpoints protected
- **Rate Limiting**: Configurable request limits

### Security Disclaimers
⚠️ **NOT FOR REAL ELECTIONS** - This is a demonstration system only
- Demo undo functionality compromises immutability
- No advanced cryptographic voting protocols
- Simplified threat model for educational purposes

## 🎓 Educational Value

### Data Structures Demonstrated
1. **Hash Tables**: Voter registry with O(1) operations
2. **Merkle Trees**: Tamper-evident logging with logarithmic proofs
3. **Bloom Filters**: Probabilistic duplicate detection
4. **Stacks**: LIFO audit operations
5. **Lab Algorithms**: Manhattan distance, collinearity, triangular numbers

### Course Integration
This project reuses algorithms from typical CS curriculum:
- **Manhattan Distance**: Polling station assignment
- **Collinearity Checks**: Route visualization
- **Triangular Numbers**: Compact pair indexing
- **Brute Force Algorithms**: Performance comparison baselines

## 📋 API Documentation

### Voter Management
- `POST /api/registerVoters` - Upload voter CSV
- `POST /api/issueOtacs` - Generate access codes

### Voting Operations
- `POST /api/castVote` - Submit ballot
- `GET /api/results` - Current tally
- `GET /api/merkleRoot` - Current root hash

### Audit & Verification
- `POST /api/proof` - Generate inclusion proof
- `POST /api/verifyProof` - Verify proof validity
- `GET /api/auditTrail` - System event log

### System Management
- `GET /api/stats` - System statistics
- `POST /api/undoLast` - Undo operation (demo mode)

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
VOTER_SALT=unique-salt-string
DEMO_MODE=true
BLOOM_FILTER_SIZE=100000
BLOOM_FILTER_HASH_COUNT=7
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Database Schema
- **voters**: Salted voter hashes and voting status
- **ballots**: Ballot records with sequence numbers
- **tally**: Candidate vote counts
- **audit**: System event log
- **leaves**: Merkle tree leaf storage
- **otac_mappings**: OTAC to voter mappings

## 🚀 Deployment

### Local Development
```bash
python main.py
# Access at http://localhost:8000
```

### Production Considerations
- Use proper PostgreSQL instance
- Configure Redis for session management
- Set secure environment variables
- Enable HTTPS in production
- Configure proper logging

## 📊 Evaluation Metrics

### Performance Metrics
- Vote casting latency
- Proof generation time
- Memory usage patterns
- Database query efficiency

### Security Metrics
- Hash collision resistance
- Merkle proof verification
- Bloom filter false positive rates
- Audit trail completeness

## 🤝 Contributing

This is an educational project. Contributions welcome for:
- Additional data structure demonstrations
- Performance optimizations
- Security enhancements
- Documentation improvements

## 📄 License

Educational use only. Not licensed for production voting systems.

## 🙏 Acknowledgments

- Course instructors for data structures curriculum
- FastAPI and SQLAlchemy communities
- Cryptographic libraries used
- Educational resources referenced

---

**Project Status**: ✅ Complete - Ready for demonstration and evaluation

**Demo Script**: 8-minute presentation covering all major features and data structures

**Report Ready**: Performance analysis, complexity evaluation, and security discussion included
