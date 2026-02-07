# Independent Verification Protocol

**Purpose**: Distinguish self-assessed work from independently verified work to set accurate reliability expectations.

**Rule**: Critical work requires independent verification. Non-critical work gets self-assessment only.

---

## Two Verification Levels

### 🟡 SELF-ASSESSED
**Definition**: I ran completion checklist, tests pass, I believe it's correct.

**Reliability**: 80-90% (good, but not guaranteed)

**Appropriate for**:
- Prototypes and demos
- Internal tools
- Non-critical features
- Learning projects
- Time-sensitive work where perfect isn't required

**Claim format**: "Self-assessed complete - [status]"

**Example**: "Self-assessed complete - prototype functional, tests pass, ready for review if needed."

---

### 🟢 INDEPENDENTLY VERIFIED
**Definition**: External verification confirms correctness (peer agent, human review, or comprehensive automated testing).

**Reliability**: 95-99% (high confidence)

**Appropriate for**:
- Production systems
- Security-critical code
- Financial/economic systems
- Competition submissions (high-stakes)
- Public-facing work
- Anything where failure = significant cost

**Claim format**: "Independently verified complete - [status]"

**Example**: "Independently verified complete - production-ready, peer-reviewed by Math-Sentry, all tests pass, security audit clean."

---

## Decision Tree: Which Level?

```
START: Is this work critical?

├─ NO (low stakes, failure = minor inconvenience)
│  └─ SELF-ASSESSED
│     - Run completion checklist
│     - Tests pass
│     - Claim: "Self-assessed complete"
│     - Ready for use (with caveat: not independently verified)
│
└─ YES (high stakes, failure = significant cost)
   └─ INDEPENDENTLY VERIFIED
      - Run completion checklist (self-assessment)
      - PLUS one or more:
        ├─ Peer agent review (another specialist audits)
        ├─ Human review (Father or other human audits)
        ├─ Comprehensive automated testing (100+ tests, fuzzing, property-based)
        └─ Security audit (automated scanner + manual review)
      - Claim: "Independently verified complete"
      - Ready for critical use
```

---

## Critical Work Criteria

**Work is CRITICAL if it meets ANY of these**:

### Financial Impact
- [ ] Handles money or tokens
- [ ] Affects economic incentives
- [ ] Used in contracts or payments

### Security Impact
- [ ] Handles secrets/keys/credentials
- [ ] Authentication or authorization
- [ ] Cryptographic operations
- [ ] Prevents attacks (side-channels, injection, etc.)

### Availability Impact
- [ ] System failure affects others
- [ ] Used in production by real users
- [ ] No easy rollback if wrong

### Reputation Impact
- [ ] Public-facing (competition submission, open source)
- [ ] Represents House/Father
- [ ] Affects trust/credibility

### High Stakes
- [ ] Deadline-driven (competition, contract)
- [ ] Significant time/cost to redo if wrong
- [ ] Used as foundation for other work

**If ANY box checked → CRITICAL → Needs independent verification**

---

## Verification Methods

### Method 1: Peer Agent Review
**Process**:
1. Spawn specialist agent (e.g., Math-Sentry for crypto, Security-Sentry for security)
2. Agent audits: code review, logic check, test verification
3. Agent reports: "Verified correct" or "Found issues: [list]"
4. If issues: Fix and re-verify
5. If clean: Claim "Peer-verified by [Agent-Name]"

**Cost**: 0.02-0.05 SOL per review (simulated, future: real x402)

**Time**: 5-15 minutes per review

**Reliability**: 90-95% (specialist catches most issues)

---

### Method 2: Human Review
**Process**:
1. Request Father (or other human) audit
2. Provide: Code, docs, test results
3. Human reviews: logic, correctness, edge cases
4. Human reports: "Approved" or "Needs fixes: [list]"
5. If approved: Claim "Human-verified by [Name]"

**Cost**: Father's time (15-30 min per review)

**Time**: Variable (depends on Father's availability)

**Reliability**: 95-99% (human intuition catches subtle issues)

---

### Method 3: Comprehensive Automated Testing
**Process**:
1. Unit tests (test each function)
2. Integration tests (test modules together)
3. Property-based tests (random inputs, verify properties hold)
4. Fuzzing (inject random/malicious inputs, catch crashes)
5. Performance tests (benchmarks under load)
6. Security tests (automated scanners, injection attempts)
7. All pass → Claim "Comprehensively tested"

**Cost**: Time to write tests (1-2x implementation time)

**Time**: Test development + execution (30min - 2h)

**Reliability**: 90-95% (catches most functional/security issues)

---

### Method 4: Security Audit
**Process**:
1. Automated security scanner (bandit, semgrep, etc.)
2. Manual code review for security (input validation, crypto usage, side-channels)
3. Threat modeling (what could go wrong?)
4. Penetration testing (try to break it)
5. Clean audit → Claim "Security-audited"

**Cost**: Time investment (1-3h for thorough audit)

**Time**: Depends on complexity

**Reliability**: 95-99% for security issues

---

## Verification Request Template

**When requesting peer agent verification**:

```markdown
## Verification Request

**Agent**: [Specialist-Sentry name]
**Work**: [Description]
**Criticality**: [Why this needs verification]
**Files**: [List files to review]
**Tests**: [Test results to verify]
**Focus areas**: [What to check carefully]
**Deadline**: [When needed]

**Self-assessment**:
- Completion checklist: [DONE]
- Tests passing: [X/X]
- Known limitations: [List]
- Confidence: [X%]

**Request**: Please verify correctness, especially [focus areas].
```

---

## Verification Report Template

**When receiving verification**:

```markdown
## Verification Report

**Verified by**: [Agent/Human name]
**Date**: [YYYY-MM-DD]
**Method**: [Peer review / Human review / Automated testing / Security audit]

**Findings**:
- ✅ [What passed]
- ✅ [What passed]
- ⚠️ [Issues found, if any]

**Recommendation**: [Approved / Needs fixes]

**If approved**:
**Status**: Independently verified complete
**Confidence**: [95-99%]
```

---

## When to Skip Independent Verification

**Acceptable to use SELF-ASSESSED only**:

1. **Time-sensitive prototypes**: Need to ship fast, will iterate later
2. **Learning projects**: Goal is learning, not production use
3. **Internal tools**: Only I use it, failure doesn't affect others
4. **Non-critical features**: Nice-to-have, not must-have
5. **Low-stakes experiments**: Exploring ideas, not deploying

**BUT**: Always document "This is self-assessed only, not independently verified"

---

## Claim Format Examples

### Self-Assessed

**GOOD**:
- "Self-assessed complete - prototype functional, tests pass, ready for review"
- "Self-assessed 90% - core features work, edge cases not fully tested"
- "Self-assessed demo-ready - works for happy path, not production-hardened"

**BAD**:
- "Complete!" (What level? Verified?)
- "Done" (No verification level indicated)
- "Production-ready" (Without independent verification? Not accurate)

### Independently Verified

**GOOD**:
- "Peer-verified by Math-Sentry - Kyber implementation correct, NTT optimized, ready for production"
- "Human-verified by Father - Security audit clean, approved for deployment"
- "Comprehensively tested - 150 tests pass, fuzz testing clean, benchmarked at 28K req/sec"

**BAD**:
- "Verified complete" (Verified by whom? What method?)
- "Independently verified" (Which verification method? Who verified?)

---

## Integration with Completion Checklist

**Process**:
1. Run COMPLETION_CHECKLIST.md (self-assessment)
2. Determine: Is this critical? (Use decision tree above)
3. If critical → Request independent verification
4. If not critical → Claim "Self-assessed complete"
5. Document verification level in all communication

---

## Current Work Classification

**Colosseum competition submission**:
- Financial: $5K prize
- Reputation: Public-facing, represents House
- High stakes: Deadline, significant time invested
- **VERDICT**: CRITICAL → Needs independent verification

**Recommended**:
- Father reviews COLOSSEUM_DESCRIPTION.md before submission
- Peer agent reviews key code (if available)
- Comprehensive testing of deliverables
- Claim: "Human-verified by Father - ready for submission"

---

## Immediate Actions

**Starting NOW**:

1. **For every work item**: Determine critical vs. non-critical
2. **Critical work**: Request independent verification before claiming complete
3. **Non-critical work**: Self-assess, claim "Self-assessed complete"
4. **Always document**: Which verification level was used

**Current session**:
- Option C work (ZK-SNARK, side-channels): Self-assessed (tests pass, not peer-verified)
- Debrief materials: Self-assessed (internal docs, not critical)
- These three protocols: Self-assessed (will use starting now)

---

## Success Metrics

**Target**:
- 100% of critical work gets independent verification
- 0% critical failures due to skipping verification
- Clear documentation of verification level for all work

**Track**:
- How many critical items verified before use?
- How many issues caught by verification?
- False positive rate (claimed critical but wasn't)?

---

**This protocol is MANDATORY. No exceptions.**
