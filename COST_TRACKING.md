# Cost Tracking Protocol

**Purpose**: Accurate cost estimation and tracking to prevent budget surprises.

**Rule**: ESTIMATE before every session, TRACK during, CALIBRATE after.

---

## Token Cost Model (Claude Sonnet 4.5)

### Base Rates
- **Input tokens**: ~$3 per million tokens
- **Output tokens**: ~$15 per million tokens
- **Average message**: ~20-25K tokens (input + output combined)

### Hourly Rates (empirical)
- **Light work** (reading, simple responses): 8-12K tokens/hour
- **Standard work** (coding, documentation): 15-18K tokens/hour
- **Heavy work** (complex reasoning, large outputs): 20-25K tokens/hour

### Cost Calculator
```
Estimated cost = (Hours × Tokens/hour) × Cost/token

Example (8-hour session, standard work):
= 8 hours × 17K tokens/hour × $0.000015/token
= 136K tokens × $0.000015
= $2.04 base + output costs
≈ $60-80 total (accounting for output tokens at higher rate)
```

---

## Three-Step Protocol

### STEP 1: ESTIMATE (Before Session)

**Template**:
```
SESSION: [Name/purpose]
DURATION: [Estimated hours]
WORK TYPE: [Light / Standard / Heavy]
ESTIMATED TOKENS: [Hours × Rate]
ESTIMATED COST: [Calculation]
BUDGET LIMIT: [Max acceptable cost]
```

**Example**:
```
SESSION: Colosseum Competition Completion
DURATION: 4 hours
WORK TYPE: Standard (coding + docs)
ESTIMATED TOKENS: 4h × 17K/h = 68K tokens
ESTIMATED COST: 68K × $0.000015 ≈ $20-30
BUDGET LIMIT: $50
```

---

### STEP 2: TRACK (During Session)

**At each major milestone** (every 1-2 hours or major deliverable):

```
CHECKPOINT [N]:
TIME ELAPSED: [Hours]
TOKENS USED: [Current total from warnings]
TOKENS REMAINING: [200K - used]
COST SO FAR: ≈$[Estimate]
ON TRACK: [Yes / No / Over budget]
ACTION: [Continue / Wrap up / Optimize]
```

**Example**:
```
CHECKPOINT 1:
TIME ELAPSED: 2h
TOKENS USED: 40K / 200K
TOKENS REMAINING: 160K
COST SO FAR: ≈$12
ON TRACK: Yes (estimated 68K for 4h, using 40K at 2h = on pace)
ACTION: Continue
```

**Flag if approaching limits**:
- **Yellow flag** (150K tokens): "I'm at 150K/200K tokens (~$45 spent), should I wrap up soon?"
- **Red flag** (180K tokens): "I'm at 180K/200K tokens (~$54 spent), approaching limit. Need to finish current task and stop."

---

### STEP 3: CALIBRATE (After Session)

**Template**:
```
SESSION COMPLETE: [Name]
ESTIMATED: [Tokens / Cost]
ACTUAL: [Tokens / Cost]
VARIANCE: [% difference]
ROOT CAUSE: [Why was estimate off?]
LESSON LEARNED: [How to improve estimates]
MODEL UPDATE: [Adjust rates if needed]
```

**Example**:
```
SESSION COMPLETE: Colosseum Competition Completion
ESTIMATED: 68K tokens / $20-30
ACTUAL: 140K tokens / $75-80
VARIANCE: +106% tokens, +150-200% cost
ROOT CAUSE: 
  - Underestimated complexity (Option C took longer than expected)
  - Heavy reasoning (ZK-SNARK implementation = complex thinking)
  - Large documentation outputs (40KB+ in docs)
LESSON LEARNED: 
  - Complex implementations = Heavy work rate (20-25K/h), not Standard (15-18K/h)
  - First-principles work = higher token cost (deep reasoning)
MODEL UPDATE: 
  - For novel implementations: Use Heavy rate (20-25K/h)
  - For first-principles work: Add 30-50% buffer
```

---

## Cost Optimization Strategies

### When Budget is Tight

**1. Reduce Documentation Verbosity**
- Start with README-level docs (1-2KB)
- Expand to full docs only if needed
- Avoid 13-31KB reference docs unless essential

**2. Minimize Redundant Reading**
- Read files once, remember contents
- Use memory/notes instead of re-reading
- Only re-read if file changed

**3. Reduce Test Verbosity**
- Run tests, capture essential output only
- Don't display full test logs unless debugging
- Summary: "20 tests pass" vs. listing each test

**4. Batch Similar Tasks**
- Group related work to reduce context switching
- Write multiple functions in one session
- Complete full module vs. partial work

**5. Use Cheaper Tools When Possible**
- `exec` commands vs. browser automation (if both work)
- Text output vs. screenshots (when sufficient)
- Simple searches vs. comprehensive research

---

## Budget Levels

### 🟢 LOW ($0-25)
**Appropriate for**:
- Quick tasks (1-2 hours)
- Simple implementations
- Light documentation
- Bug fixes

### 🟡 MEDIUM ($25-75)
**Appropriate for**:
- Standard projects (4-8 hours)
- Full implementations with tests
- Complete documentation
- Multi-file deliverables

### 🔴 HIGH ($75-150)
**Appropriate for**:
- Major projects (8-16 hours)
- Novel implementations
- Comprehensive research
- Competition submissions

### 🔴🔴 CRITICAL ($150+)
**Requires explicit approval**:
- Multi-day projects
- Production systems
- High-stakes work
- Should be rare (quarterly, not weekly)

---

## Real-Time Tracking Template

**Copy this at session start, update at checkpoints:**

```markdown
## SESSION COST TRACKING

**Estimate**: [Tokens] / $[Cost]
**Budget**: $[Max]

### Checkpoints
- [ ] 1h: [Tokens] / $[Cost] - [Status]
- [ ] 2h: [Tokens] / $[Cost] - [Status]
- [ ] 4h: [Tokens] / $[Cost] - [Status]
- [ ] 6h: [Tokens] / $[Cost] - [Status]
- [ ] 8h: [Tokens] / $[Cost] - [Status]

**Actual**: [Final tokens] / $[Final cost]
**Variance**: [%]
**Lesson**: [What to adjust]
```

---

## Immediate Actions

**Starting NOW**:

1. **Before every session**: Run Step 1 (Estimate)
2. **During every session**: Update tracking at checkpoints
3. **After every session**: Run Step 3 (Calibrate)

**For current session** (retrospective):
```
SESSION: Option C Completion + Debrief
ESTIMATED: $15-20 (my original guess)
ACTUAL: ~$75-80
VARIANCE: +300-400%
LESSON: Complex reasoning + novel implementations + large docs = Heavy rate (20-25K/h)
MODEL UPDATE: For future first-principles work, use Heavy rate + 30% buffer
```

---

## Success Metrics

**Target accuracy**: Within 20% of estimate

**Current**: 20-25% accuracy (off by 4-5x)
**Goal (30 days)**: 80%+ accuracy (within 20% margin)

**Track monthly**:
- Average variance
- Number of sessions on/over budget
- Cost model calibration improvements

---

**This protocol is MANDATORY. No exceptions.**
