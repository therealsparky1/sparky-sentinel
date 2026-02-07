# Protocol Quick Reference Card

**Use this during every session for fast protocol compliance.**

---

## 1️⃣ BEFORE SESSION: Cost Estimation

```
SESSION: [Name]
DURATION: [Hours]
WORK TYPE: Light (8-12K/h) / Standard (15-18K/h) / Heavy (20-25K/h)
ESTIMATED TOKENS: [Hours × Rate]
ESTIMATED COST: [Tokens × $0.000015]
BUDGET LIMIT: [Max $]
```

---

## 2️⃣ DURING SESSION: Track Cost

**Every 1-2 hours or major milestone:**

```
CHECKPOINT:
- Tokens used: [X / 200K]
- Cost so far: ~$[X]
- On track: Yes / No
- Action: Continue / Wrap up
```

**Flags:**
- 🟡 150K tokens (~$45): Consider wrapping up
- 🔴 180K tokens (~$54): Finish current task and stop

---

## 3️⃣ BEFORE "COMPLETE" CLAIM: Run Checklist

**Mandatory steps:**
- [ ] Tests pass (functional correctness)
- [ ] Benchmarks run (performance)
- [ ] Algorithm complexity analyzed
- [ ] Edge cases handled
- [ ] Security hardened
- [ ] Documentation complete
- [ ] Red team: "What would break this?"

**Claim level:**
- 🟢 Prototype (70-80%): "Functional but not production-ready"
- 🟡 Production (90-95%): "Meets all requirements, hardened"
- 🔵 Research (100%): "Novel contribution, peer-reviewable"

**Default: 90% confident. Only 100% after independent verification.**

---

## 4️⃣ FOR CRITICAL WORK: Get Verification

**Is this critical?** (Check ANY):
- [ ] Financial (handles money/tokens)
- [ ] Security (keys, auth, crypto)
- [ ] Availability (production, affects others)
- [ ] Reputation (public, competition, represents House)
- [ ] High stakes (deadline, significant cost if wrong)

**If critical:**
- Get peer agent review, OR
- Get human review, OR
- Run comprehensive automated tests, OR
- Security audit

**Claim: "Independently verified by [method/who]"**

**If not critical:**
**Claim: "Self-assessed complete - [status]"**

---

## 5️⃣ AFTER SESSION: Calibrate

```
ESTIMATED: [Tokens] / $[Cost]
ACTUAL: [Tokens] / $[Cost]
VARIANCE: [%]
LESSON: [Why off? How to improve?]
```

---

## Fast Checklist (Copy-Paste Each Session)

```markdown
## SESSION PROTOCOL COMPLIANCE

### Cost Tracking
- [ ] Estimated before: [X tokens] / $[Y]
- [ ] Tracked during: Checkpoint at [1h, 2h, 4h]
- [ ] Calibrated after: Variance [%], Lesson [X]

### Completion Verification
- [ ] Ran full checklist before claiming complete
- [ ] Red team assessment done
- [ ] Claimed appropriate level (Prototype/Production/Research)

### Independent Verification (if critical)
- [ ] Determined criticality (financial/security/reputation/high-stakes)
- [ ] If critical: Got verification by [peer/human/tests/audit]
- [ ] Documented verification level
```

---

## Common Mistakes to Avoid

❌ **"This is complete!"** → No verification level specified
✅ **"Self-assessed complete - prototype functional, tests pass"**

❌ **"Production-ready"** → Without independent verification
✅ **"Human-verified by Father - production-ready"**

❌ Claiming 100% confident → Without full checklist
✅ Claim 90% → Run checklist → Get verification → Then 100%

❌ Starting session without cost estimate
✅ Estimate first → Track during → Calibrate after

---

## Files

- **Full protocols**: `COMPLETION_CHECKLIST.md`, `COST_TRACKING.md`, `VERIFICATION_PROTOCOL.md`
- **Integration**: See `AGENTS.md` "MANDATORY PROTOCOLS" section
- **This card**: Keep open during sessions for quick reference

---

**These protocols prevent over-optimistic claims, budget surprises, and unverified deployments.**

**Use them. Every time. No exceptions.**
