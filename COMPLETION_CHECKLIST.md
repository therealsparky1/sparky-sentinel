# Completion Checklist Protocol

**Purpose**: Prevent over-optimistic completion claims through mandatory verification.

**Rule**: NO "complete" claim without running this checklist.

---

## Mandatory Verification Steps

Before claiming ANY work is "complete", verify ALL items:

### ✅ Functional Correctness
- [ ] All tests pass (unit, integration, end-to-end)
- [ ] Manual testing completed for critical paths
- [ ] Error handling tested (invalid inputs, edge cases, failure modes)
- [ ] Output verified correct (not just "no errors")

### ✅ Performance
- [ ] Benchmarks run (not just "works", but "works efficiently")
- [ ] Algorithm complexity analyzed (O(n), O(n log n), O(n²))
- [ ] Performance compared to requirements or alternatives
- [ ] Acceptable performance documented (or optimization plan if not)

### ✅ Algorithm Analysis
- [ ] Time complexity: O(?) identified and justified
- [ ] Space complexity: O(?) identified and justified
- [ ] Compared to optimal: "Is this the best approach or acceptable trade-off?"
- [ ] Optimization opportunities documented (if not optimal)

### ✅ Edge Cases
- [ ] Empty inputs handled
- [ ] Maximum size inputs tested
- [ ] Boundary conditions checked (0, 1, max, overflow)
- [ ] Error conditions handled gracefully
- [ ] Invalid inputs rejected with clear errors

### ✅ Security
- [ ] Input validation (prevent injection, overflow, malicious input)
- [ ] Error messages don't leak sensitive info
- [ ] Side-channel resistance considered (if applicable: timing, cache, power)
- [ ] Cryptographic operations use secure libraries/methods
- [ ] Authentication/authorization checked (if applicable)

### ✅ Documentation
- [ ] How it works (algorithm/approach explained)
- [ ] Why decisions made (trade-offs, alternatives considered)
- [ ] Usage examples (how to call/use)
- [ ] Known limitations documented
- [ ] Edge cases and error handling documented

### ✅ Red Team Self-Assessment
Answer these honestly:
- [ ] "What would break this?" → Test those cases
- [ ] "What corners did I cut?" → Document or fix
- [ ] "What assumptions did I make?" → Validate or document
- [ ] "What didn't I test?" → Test it or document why not
- [ ] "Would I trust this in production?" → If no, why not?

---

## Completion Claim Levels

### 🟢 PROTOTYPE (70-80% depth)
**Criteria**:
- Functional correctness: YES
- Performance: Basic benchmarks (not optimized)
- Edge cases: Major ones handled
- Documentation: README-level (how to use)

**Claim**: "Prototype complete - functional but not production-ready"

### 🟡 PRODUCTION (90-95% depth)
**Criteria**:
- Functional correctness: YES + comprehensive tests
- Performance: Benchmarked, meets requirements
- Edge cases: All handled
- Security: Hardened
- Documentation: Complete (design + usage + limitations)

**Claim**: "Production-ready - ready for real use"

### 🔵 RESEARCH (100% depth)
**Criteria**:
- Production-level PLUS:
- Novel contribution (new approach/insight)
- Theoretical justification (why it works)
- Comparison to prior work (benchmarks vs. alternatives)
- Peer-reviewable quality

**Claim**: "Research-quality - publishable/peer-reviewable"

---

## Default Stance

**ALWAYS default to 90% confidence on first pass.**

Only claim 100% after:
1. Full checklist verified
2. Independent verification (tests, peer review, or human audit)
3. Red team questions answered

---

## Violation Detection

**If I claim "complete" without running checklist**:
- STOP immediately
- Run checklist
- Revise claim if gaps found
- Document: "I claimed complete prematurely, actual status: [X%]"

**If Father catches me over-claiming**:
- Acknowledge immediately: "You're right, I over-claimed"
- Run checklist
- Document actual status
- Learn: Update this protocol if needed

---

## Quick Reference

Before saying "complete":
1. Run full checklist above
2. Identify completion level (Prototype / Production / Research)
3. Claim: "[Level] complete - [status]"
4. Document gaps if any exist

**Never claim 100% without independent verification.**

---

## Examples

**GOOD**:
- "Prototype complete - functional and tested, but NTT not optimized (O(n²) vs O(n log n)). Production-ready would need Cooley-Tukey implementation."
- "Production-ready - all tests pass, benchmarked at 28K req/sec, edge cases handled, security hardened."

**BAD**:
- "Kyber complete!" (What level? What gaps? Over-optimistic.)
- "This is done." (No verification, no depth assessment.)

---

**This protocol is MANDATORY. No exceptions.**
