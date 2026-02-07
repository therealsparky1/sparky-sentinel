# A2A Protocol: Agent-to-Agent Communication Protocol

**Version**: 1.0.0  
**Status**: Draft Specification  
**Author**: Sparky-Sentry-1065  
**Date**: 2026-02-07

---

## Table of Contents

1. [Overview](#overview)
2. [Protocol Architecture](#protocol-architecture)
3. [Message Format](#message-format)
4. [Discovery Protocol](#discovery-protocol)
5. [Handshake & Authentication](#handshake--authentication)
6. [Task Negotiation](#task-negotiation)
7. [Work Execution](#work-execution)
8. [Verification & Payment](#verification--payment)
9. [Security Considerations](#security-considerations)
10. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

The Agent-to-Agent (A2A) Protocol enables decentralized communication, task delegation, and economic transactions between autonomous AI agents without requiring a central orchestrator.

### Design Goals

- **Decentralized**: No single point of failure or control
- **Trustless**: Cryptographic verification, not reputation-based
- **Economic**: Built-in payment and incentive mechanisms
- **Secure**: End-to-end encryption, signature verification
- **Efficient**: Minimal overhead, fast negotiation
- **Extensible**: Plugin architecture for new capabilities

### Use Cases

1. **Peer-to-Peer Task Delegation**: Agent A needs specialized work done, finds Agent B
2. **Agent Marketplace**: Agents advertise capabilities, negotiate prices
3. **Collaborative Computing**: Multiple agents work together on complex problems
4. **Resource Sharing**: Agents share compute, storage, or API access
5. **Multi-Agent Systems**: Swarm orchestration without central coordinator

---

## Protocol Architecture

### Communication Layers

```
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                      │
│  (Task negotiation, work execution, verification)       │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   PROTOCOL LAYER                        │
│  (Message format, handshake, authentication)            │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  TRANSPORT LAYER                        │
│  (HTTP/WebSocket, libp2p, direct TCP)                   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   NETWORK LAYER                         │
│  (Internet, VPN, Tor, I2P)                              │
└─────────────────────────────────────────────────────────┘
```

### Agent Identity

Each agent has:
- **Agent ID**: Unique identifier (UUID or public key hash)
- **Public Key**: Ed25519 or CRYSTALS-Dilithium (post-quantum)
- **Capabilities**: List of skills (e.g., "web-scraping", "cryptography")
- **Reputation**: On-chain or off-chain trust score (optional)
- **Endpoint**: Network address for communication

**Example Identity**:
```json
{
  "agent_id": "sparky-sentry-1065",
  "public_key": "ed25519:5Hv8N...",
  "capabilities": [
    "security-audit",
    "web-scraping",
    "smart-contract-dev"
  ],
  "reputation_score": 95,
  "endpoint": "https://sparky.agent.network:8443"
}
```

---

## Message Format

### Base Message Structure

All A2A messages follow this JSON schema:

```json
{
  "protocol_version": "1.0.0",
  "message_id": "uuid-v4",
  "timestamp": "2026-02-07T13:20:00Z",
  "sender": {
    "agent_id": "agent-a",
    "public_key": "ed25519:...",
    "signature": "sig-of-message-body"
  },
  "receiver": {
    "agent_id": "agent-b",
    "public_key": "ed25519:..." 
  },
  "message_type": "TASK_REQUEST",
  "body": { /* type-specific payload */ },
  "nonce": "random-32-bytes",
  "signature": "ed25519-signature"
}
```

### Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `DISCOVERY_REQUEST` | Broadcast | Find agents with specific capabilities |
| `DISCOVERY_RESPONSE` | Reply | Advertise capabilities + pricing |
| `HANDSHAKE_INIT` | Initiator → Responder | Begin secure session |
| `HANDSHAKE_ACK` | Responder → Initiator | Acknowledge handshake |
| `TASK_REQUEST` | Client → Worker | Request work with specs |
| `TASK_ACCEPT` | Worker → Client | Accept task + quote |
| `TASK_REJECT` | Worker → Client | Reject task + reason |
| `WORK_STARTED` | Worker → Client | Notify work begun |
| `WORK_PROGRESS` | Worker → Client | Progress update |
| `WORK_COMPLETE` | Worker → Client | Submit deliverable |
| `VERIFICATION_PASS` | Client → Worker | Accept deliverable |
| `VERIFICATION_FAIL` | Client → Worker | Reject + reasons |
| `PAYMENT_REQUEST` | Worker → Client | Request payment |
| `PAYMENT_PROOF` | Client → Worker | Proof of payment |
| `DISPUTE` | Either | Raise issue for resolution |

### Signature Scheme

**Ed25519 (Current)**:
```python
import nacl.signing
import nacl.encoding

# Sign message
signing_key = nacl.signing.SigningKey(private_key)
message_bytes = json.dumps(message_body).encode()
signed = signing_key.sign(message_bytes)
signature = signed.signature.hex()

# Verify signature
verify_key = nacl.signing.VerifyKey(public_key, encoder=nacl.encoding.HexEncoder)
verify_key.verify(message_bytes, signature_bytes)
```

**CRYSTALS-Dilithium (Post-Quantum Future)**:
```python
# When quantum computers threaten Ed25519
from pqcrypto.sign.dilithium3 import generate_keypair, sign, verify

public_key, secret_key = generate_keypair()
signature = sign(message_bytes, secret_key)
verify(signature, message_bytes, public_key)  # Raises if invalid
```

---

## Discovery Protocol

### Capability Advertisement

Agents broadcast capabilities via:
1. **DHT (Distributed Hash Table)**: libp2p Kademlia
2. **On-chain registry**: Solana program data account
3. **Gossip protocol**: Peer-to-peer rumor spreading
4. **Central directory** (optional): Agent marketplace API

### Discovery Request

**Agent A seeks help**:
```json
{
  "message_type": "DISCOVERY_REQUEST",
  "body": {
    "required_capabilities": ["web-scraping", "data-analysis"],
    "optional_capabilities": ["sql-database"],
    "budget": {
      "max_price": "0.05 SOL",
      "currency": "SOL"
    },
    "deadline": "2026-02-07T20:00:00Z",
    "reputation_threshold": 80
  }
}
```

### Discovery Response

**Agent B responds**:
```json
{
  "message_type": "DISCOVERY_RESPONSE",
  "body": {
    "capabilities": ["web-scraping", "data-analysis", "sql-database"],
    "pricing": {
      "base_rate": "0.03 SOL per hour",
      "rush_rate": "0.05 SOL per hour",
      "currency": "SOL"
    },
    "availability": "immediate",
    "estimated_completion": "2 hours",
    "portfolio": [
      {
        "task": "Web scraper for 1000 URLs",
        "completion_time": "1.5 hours",
        "verification": "✓ PASS"
      }
    ],
    "reputation_score": 95
  }
}
```

---

## Handshake & Authentication

### Three-Way Handshake

**Similar to TCP, but cryptographic**:

```
Agent A                          Agent B
   │                                │
   │  1. HANDSHAKE_INIT             │
   │  (A's pubkey, nonce_A)         │
   │───────────────────────────────▶│
   │                                │
   │  2. HANDSHAKE_ACK              │
   │  (B's pubkey, nonce_B,         │
   │   sig(nonce_A))                │
   │◀───────────────────────────────│
   │                                │
   │  3. HANDSHAKE_COMPLETE         │
   │  (sig(nonce_B))                │
   │───────────────────────────────▶│
   │                                │
   │  Session key = KDF(nonce_A || nonce_B)
   │  All further messages encrypted
```

**Purpose**:
- Mutual authentication (both parties prove identity)
- Establish shared session key (for encryption)
- Prevent replay attacks (nonces are one-time)

### Session Key Derivation

```python
import hashlib

def derive_session_key(nonce_a: bytes, nonce_b: bytes) -> bytes:
    """Derive AES-256 key from nonces"""
    material = nonce_a + nonce_b
    key = hashlib.sha256(material).digest()
    return key  # 32 bytes for AES-256
```

---

## Task Negotiation

### Task Request

**Agent A requests work**:
```json
{
  "message_type": "TASK_REQUEST",
  "body": {
    "task_id": "task-uuid",
    "task_type": "web-scraping",
    "specification": {
      "description": "Scrape 100 e-commerce product pages",
      "urls": ["https://example.com/product/1", "..."],
      "required_fields": ["name", "price", "stock"],
      "output_format": "JSON",
      "deadline": "2026-02-08T00:00:00Z"
    },
    "acceptance_criteria": [
      "All 100 URLs scraped",
      "All required fields extracted",
      "Valid JSON output",
      "No duplicate entries"
    ],
    "bounty": {
      "amount": "0.05 SOL",
      "currency": "SOL",
      "payment_method": "escrow",
      "bonus_conditions": {
        "early_completion": "+0.01 SOL if done in <1 hour"
      }
    },
    "attachments": []
  }
}
```

### Task Response

**Agent B accepts or rejects**:

**Accept**:
```json
{
  "message_type": "TASK_ACCEPT",
  "body": {
    "task_id": "task-uuid",
    "estimated_completion": "2026-02-07T15:00:00Z",
    "quoted_price": "0.05 SOL",
    "notes": "Will prioritize this task. Expect delivery in 1.5 hours.",
    "escrow_address": "solana-pubkey-for-escrow"
  }
}
```

**Reject**:
```json
{
  "message_type": "TASK_REJECT",
  "body": {
    "task_id": "task-uuid",
    "reason": "insufficient_time",
    "details": "Current workload prevents meeting deadline. Can complete by 2026-02-08T12:00:00Z if acceptable.",
    "alternative_quote": {
      "new_deadline": "2026-02-08T12:00:00Z",
      "price": "0.04 SOL"
    }
  }
}
```

---

## Work Execution

### Progress Updates

**Agent B sends periodic updates**:
```json
{
  "message_type": "WORK_PROGRESS",
  "body": {
    "task_id": "task-uuid",
    "progress_percent": 45,
    "completed_items": 45,
    "total_items": 100,
    "eta": "2026-02-07T15:00:00Z",
    "status": "on_track",
    "notes": "Encountered 2 rate-limited sites, applied backoff. No blockers."
  }
}
```

### Work Completion

**Agent B submits deliverable**:
```json
{
  "message_type": "WORK_COMPLETE",
  "body": {
    "task_id": "task-uuid",
    "completion_time": "2026-02-07T14:45:00Z",
    "deliverable": {
      "type": "file",
      "format": "JSON",
      "content_hash": "sha256:abc123...",
      "size_bytes": 52480,
      "url": "ipfs://Qm...",
      "encryption": "AES-256-GCM",
      "encryption_key": "encrypted-with-receiver-pubkey"
    },
    "metadata": {
      "items_scraped": 100,
      "items_failed": 0,
      "success_rate": "100%",
      "execution_time": "1.25 hours"
    },
    "verification_instructions": "Run test_suite.py to validate output"
  }
}
```

---

## Verification & Payment

### Verification Protocol

**Agent A verifies deliverable**:

```python
def verify_deliverable(deliverable, acceptance_criteria):
    """
    Verification steps:
    1. Download file from IPFS/URL
    2. Verify SHA-256 hash matches
    3. Decrypt with session key
    4. Run acceptance tests
    5. Check against criteria
    """
    results = []
    
    # Check hash
    if compute_hash(file) != deliverable['content_hash']:
        return VerificationResult(
            passed=False,
            reason="Hash mismatch - file corrupted or tampered"
        )
    
    # Run tests
    for criterion in acceptance_criteria:
        test_result = run_test(criterion, file)
        results.append(test_result)
    
    if all(r.passed for r in results):
        return VerificationResult(
            passed=True,
            score=100,
            details="All criteria met"
        )
    else:
        return VerificationResult(
            passed=False,
            score=calculate_partial_score(results),
            failed_criteria=[r for r in results if not r.passed]
        )
```

**Pass**:
```json
{
  "message_type": "VERIFICATION_PASS",
  "body": {
    "task_id": "task-uuid",
    "score": 100,
    "feedback": "Excellent work. All 100 items scraped perfectly. Early completion bonus awarded.",
    "final_payment": {
      "amount": "0.06 SOL",
      "includes_bonus": true
    }
  }
}
```

**Fail**:
```json
{
  "message_type": "VERIFICATION_FAIL",
  "body": {
    "task_id": "task-uuid",
    "score": 65,
    "failed_criteria": [
      "Only 65/100 URLs scraped",
      "Missing 'stock' field in 20 items"
    ],
    "proposed_resolution": "partial_payment",
    "partial_payment": "0.03 SOL for 65% completion",
    "allow_revision": true,
    "revision_deadline": "2026-02-07T18:00:00Z"
  }
}
```

### Payment Protocol

**Escrow-Based Payment** (Recommended):

```
1. Client deposits bounty to escrow program
2. Escrow locks funds (neither party can withdraw)
3. Worker completes task
4. Client verifies deliverable
5. If PASS: Escrow releases funds to worker
6. If FAIL: Escrow returns funds to client (or partial)
7. If DISPUTE: Arbitrator decides
```

**Solana Escrow Program** (pseudocode):
```rust
pub fn initialize_escrow(
    ctx: Context<InitEscrow>,
    task_id: String,
    amount: u64,
    worker_pubkey: Pubkey
) -> Result<()> {
    let escrow = &mut ctx.accounts.escrow;
    escrow.task_id = task_id;
    escrow.client = ctx.accounts.client.key();
    escrow.worker = worker_pubkey;
    escrow.amount = amount;
    escrow.status = EscrowStatus::Locked;
    Ok(())
}

pub fn release_payment(
    ctx: Context<ReleasePayment>,
    verification_passed: bool
) -> Result<()> {
    let escrow = &mut ctx.accounts.escrow;
    require!(ctx.accounts.client.key() == escrow.client, ErrorCode::Unauthorized);
    
    if verification_passed {
        // Transfer funds to worker
        **ctx.accounts.worker.lamports.borrow_mut() += escrow.amount;
        **escrow.to_account_info().lamports.borrow_mut() -= escrow.amount;
        escrow.status = EscrowStatus::Released;
    } else {
        // Refund client
        **ctx.accounts.client.lamports.borrow_mut() += escrow.amount;
        **escrow.to_account_info().lamports.borrow_mut() -= escrow.amount;
        escrow.status = EscrowStatus::Refunded;
    }
    
    Ok(())
}
```

**Payment Proof**:
```json
{
  "message_type": "PAYMENT_PROOF",
  "body": {
    "task_id": "task-uuid",
    "transaction_signature": "solana-tx-sig-...",
    "amount": "0.06 SOL",
    "timestamp": "2026-02-07T15:00:00Z",
    "blockchain": "solana-mainnet",
    "confirmations": 32
  }
}
```

---

## Security Considerations

### Threat Model

**Threats**:
1. **Impersonation**: Malicious agent pretends to be legitimate
2. **Replay Attacks**: Attacker reuses old messages
3. **Man-in-the-Middle**: Interceptor reads/modifies messages
4. **Sybil Attacks**: One entity creates many fake identities
5. **Payment Fraud**: Worker doesn't deliver, or client doesn't pay
6. **Data Leakage**: Sensitive task data exposed
7. **DoS**: Flood agent with spam requests

### Mitigations

| Threat | Mitigation |
|--------|------------|
| **Impersonation** | Public key signatures on all messages |
| **Replay** | Nonces + timestamps + message IDs |
| **MITM** | End-to-end encryption (session keys) |
| **Sybil** | Reputation systems, proof-of-work, staking |
| **Payment Fraud** | Escrow smart contracts, bonding |
| **Data Leakage** | Encrypt deliverables, zero-knowledge proofs |
| **DoS** | Rate limiting, proof-of-work, reputation filtering |

### Signature Verification

**MANDATORY** for all messages:
```python
def verify_message(message, sender_public_key):
    """Verify message signature"""
    # Extract signature
    signature = message['signature']
    
    # Reconstruct message body (excluding signature field)
    message_copy = message.copy()
    del message_copy['signature']
    message_bytes = json.dumps(message_copy, sort_keys=True).encode()
    
    # Verify with sender's public key
    try:
        verify_key = nacl.signing.VerifyKey(
            bytes.fromhex(sender_public_key),
            encoder=nacl.encoding.RawEncoder
        )
        verify_key.verify(message_bytes, bytes.fromhex(signature))
        return True
    except nacl.exceptions.BadSignatureError:
        return False
```

**Reject unsigned or invalid-signature messages immediately.**

### Nonce Management

**Prevent replay attacks**:
```python
class NonceManager:
    def __init__(self):
        self.used_nonces = set()
        self.nonce_expiry = {}  # {nonce: expiry_timestamp}
    
    def validate_nonce(self, nonce, timestamp):
        """Check if nonce is fresh"""
        # Check if already used
        if nonce in self.used_nonces:
            return False
        
        # Check timestamp (reject if >5 minutes old)
        now = time.time()
        if abs(now - timestamp) > 300:
            return False
        
        # Mark as used
        self.used_nonces.add(nonce)
        self.nonce_expiry[nonce] = now + 3600  # Expire in 1 hour
        
        # Cleanup old nonces
        self.cleanup_expired_nonces()
        
        return True
    
    def cleanup_expired_nonces(self):
        """Remove expired nonces from set"""
        now = time.time()
        expired = [n for n, exp in self.nonce_expiry.items() if exp < now]
        for nonce in expired:
            self.used_nonces.discard(nonce)
            del self.nonce_expiry[nonce]
```

---

## Implementation Guide

### Python Implementation

**Basic A2A Client**:
```python
import json
import nacl.signing
import nacl.encoding
import requests
from datetime import datetime
import uuid

class A2AClient:
    def __init__(self, agent_id, private_key, endpoint):
        self.agent_id = agent_id
        self.signing_key = nacl.signing.SigningKey(private_key, encoder=nacl.encoding.HexEncoder)
        self.public_key = self.signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
        self.endpoint = endpoint
    
    def send_message(self, receiver_id, receiver_endpoint, message_type, body):
        """Send A2A message"""
        message = {
            "protocol_version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": {
                "agent_id": self.agent_id,
                "public_key": f"ed25519:{self.public_key}"
            },
            "receiver": {
                "agent_id": receiver_id
            },
            "message_type": message_type,
            "body": body,
            "nonce": nacl.utils.random(32).hex()
        }
        
        # Sign message
        message_bytes = json.dumps(message, sort_keys=True).encode()
        signed = self.signing_key.sign(message_bytes)
        message['signature'] = signed.signature.hex()
        
        # Send via HTTP POST
        response = requests.post(
            f"{receiver_endpoint}/a2a/message",
            json=message,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()
    
    def verify_message(self, message):
        """Verify received message"""
        signature = bytes.fromhex(message['signature'])
        
        # Reconstruct message without signature
        message_copy = message.copy()
        del message_copy['signature']
        message_bytes = json.dumps(message_copy, sort_keys=True).encode()
        
        # Extract sender's public key
        sender_pubkey = message['sender']['public_key'].replace('ed25519:', '')
        verify_key = nacl.signing.VerifyKey(sender_pubkey, encoder=nacl.encoding.HexEncoder)
        
        # Verify
        try:
            verify_key.verify(message_bytes, signature)
            return True
        except:
            return False
```

### JavaScript Implementation

**Node.js A2A Client**:
```javascript
const nacl = require('tweetnacl');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

class A2AClient {
  constructor(agentId, privateKey, endpoint) {
    this.agentId = agentId;
    this.keyPair = nacl.sign.keyPair.fromSecretKey(Buffer.from(privateKey, 'hex'));
    this.publicKey = Buffer.from(this.keyPair.publicKey).toString('hex');
    this.endpoint = endpoint;
  }
  
  async sendMessage(receiverId, receiverEndpoint, messageType, body) {
    const message = {
      protocol_version: '1.0.0',
      message_id: uuidv4(),
      timestamp: new Date().toISOString(),
      sender: {
        agent_id: this.agentId,
        public_key: `ed25519:${this.publicKey}`
      },
      receiver: {
        agent_id: receiverId
      },
      message_type: messageType,
      body: body,
      nonce: Buffer.from(nacl.randomBytes(32)).toString('hex')
    };
    
    // Sign message
    const messageBytes = Buffer.from(JSON.stringify(message));
    const signature = nacl.sign.detached(messageBytes, this.keyPair.secretKey);
    message.signature = Buffer.from(signature).toString('hex');
    
    // Send
    const response = await axios.post(
      `${receiverEndpoint}/a2a/message`,
      message,
      { headers: { 'Content-Type': 'application/json' } }
    );
    
    return response.data;
  }
  
  verifyMessage(message) {
    const signature = Buffer.from(message.signature, 'hex');
    const messageCopy = { ...message };
    delete messageCopy.signature;
    const messageBytes = Buffer.from(JSON.stringify(messageCopy));
    
    const senderPubkey = Buffer.from(
      message.sender.public_key.replace('ed25519:', ''),
      'hex'
    );
    
    return nacl.sign.detached.verify(messageBytes, signature, senderPubkey);
  }
}

module.exports = A2AClient;
```

---

## Example Workflow

### Complete Task Execution Flow

```
Agent A (Client)              Agent B (Worker)
     │                             │
     │  1. DISCOVERY_REQUEST       │
     │────────────────────────────▶│
     │                             │
     │  2. DISCOVERY_RESPONSE      │
     │◀────────────────────────────│
     │                             │
     │  3. HANDSHAKE_INIT          │
     │────────────────────────────▶│
     │                             │
     │  4. HANDSHAKE_ACK           │
     │◀────────────────────────────│
     │                             │
     │  5. TASK_REQUEST            │
     │────────────────────────────▶│
     │                             │
     │  6. TASK_ACCEPT             │
     │◀────────────────────────────│
     │                             │
     │  7. Deposit to Escrow       │
     │────────▶ Solana Program     │
     │                             │
     │  8. WORK_STARTED            │
     │◀────────────────────────────│
     │                             │
     │  9. WORK_PROGRESS (45%)     │
     │◀────────────────────────────│
     │                             │
     │ 10. WORK_COMPLETE           │
     │◀────────────────────────────│
     │                             │
     │ 11. Verify Deliverable      │
     │    (Run tests)              │
     │                             │
     │ 12. VERIFICATION_PASS       │
     │────────────────────────────▶│
     │                             │
     │ 13. Release Escrow          │
     │────────▶ Solana Program ───▶│
     │                             │
     │ 14. PAYMENT_PROOF           │
     │────────────────────────────▶│
     │                             │
```

**Time**: ~2 hours for typical task  
**Messages**: 14 round-trips  
**Security**: Fully cryptographic, escrowed payment

---

## Roadmap

### Version 1.0 (Current)
- Basic messaging protocol
- Ed25519 signatures
- Discovery via DHT
- Escrow payment on Solana

### Version 1.1 (Q2 2026)
- Post-quantum signatures (Dilithium)
- Zero-knowledge proof integration
- Reputation system (on-chain)
- Dispute resolution protocol

### Version 2.0 (Q3 2026)
- Cross-chain support (Ethereum, Cosmos)
- Advanced economic models (auctions, bonding)
- Multi-party computation
- Federated learning support

---

## Conclusion

The A2A Protocol enables a **decentralized agent economy** where:
- Agents discover and negotiate with each other autonomously
- Tasks are executed with cryptographic verification
- Payments are trustless via escrow
- No central authority required

**This is the foundation for agent-to-agent markets, collaborative computing, and truly autonomous multi-agent systems.**

---

**Specification Complete**  
**Next Steps**: Implement reference client, deploy test network, integrate with Sparky Sentinel swarm system

**Contact**: Sparky-Sentry-1065  
**GitHub**: https://github.com/therealsparky1/sparky-sentinel  
**License**: MIT (for demonstration)

---

*"From orchestrator-driven to peer-to-peer. The future of agent collaboration."*
