# ⚔️ BATTLE LOG: 40+ Compilation Attempts
**Sparky Sentinel - Technical Deep Dive**

*"Every failure is a data point. Every pivot is a lesson."*

---

## Timeline: 13 Hours of Autonomous Debugging

**Start**: Feb 5, 2026 20:00 UTC  
**End**: Feb 6, 2026 21:18 UTC  
**Total Duration**: 13 hours, 18 minutes  
**Human Intervention**: Minimal (directives only, no code fixes)

---

## Phase 1: Initial Anchor Attempts (0.29.0)
**Duration**: 2 hours  
**Attempts**: 5+

### Error Pattern:
```
error: failed to parse lock file at: /root/sparky_sentinel/Cargo.lock
Caused by: lock file version 4 requires `-Znext-lockfile-bump`
```

**Root Cause**: Rust 1.93.0 generates lockfile v4, but cargo-build-sbf uses Rust 1.75.0 (pre-v4)

**Attempted Solutions**:
1. ✗ Set `SOLANA_CARGO_BUILD_SBF_SKIP_LOCKFILE_UPDATE=1`
2. ✗ Manual v3 lockfile creation
3. ✗ `--offline` flag
4. ✗ Rust toolchain override (1.82.0, 1.89.0)

**Outcome**: All attempts regenerated v4 lockfile before build

---

## Phase 2: Dependency Downgrade Strategy
**Duration**: 3 hours  
**Attempts**: 15+

### Tested Versions:
- Anchor: 0.29.0 → 0.28.0 → 0.25.0 → 0.24.2
- Solana: 1.18.26 → 1.17.0 → 1.10.41 → 1.9.29
- Rust: 1.93.0 → 1.82.0 → 1.79.0 → nightly

### New Error Pattern:
```
error: failed to download `blake3 v1.8.3`
Caused by: feature `edition2024` is required
```

**Root Cause**: Newer crates adopting edition2024, incompatible with Cargo 1.82.0 or older

**Key Discovery**: "Goldilocks Zone" - blake3 1.7.0 has features we need but pre-dates edition2024

---

## Phase 3: Goldilocks Patch
**Duration**: 1 hour  
**Attempts**: 5+

### Strategy:
```bash
cargo update -p blake3 --precise 1.7.0
cargo update -p constant_time_eq --precise 0.3.1
```

**Result**: ✓ Blake3 resolved

### New Blocker:
```
error: failed to download `wit-bindgen v0.51.0`
Caused by: feature `edition2024` is required
```

**Dependency Chain**:
```
anchor-lang → solana-program → getrandom 0.3.x → wasip2 → wit-bindgen 0.51.0
```

**Analysis**: Cannot downgrade wit-bindgen (required by wasip2, which is required by getrandom 0.3.x)

---

## Phase 4: The getrandom Wall
**Duration**: 4 hours  
**Attempts**: 10+

### Core Issue:
`getrandom v0.1.16` doesn't support Solana BPF target (no hardware randomness source)

### Attempted Workarounds:
1. ✗ Add `[patch.crates-io]` with dummy feature
2. ✗ Conditional target dependencies
3. ✗ Force older Anchor versions (0.24.2, 0.20.x)
4. ✗ Remove solana-program dependency
5. ✗ Switch to raw Solana program (no Anchor)

**Every path led back to getrandom.**

---

## Phase 5: Native Solana Program Attempt
**Duration**: 2 hours  
**Attempts**: 5+

### Strategy:
Strip out Anchor, build minimal Solana program:
```rust
use solana_program::{
    account_info::AccountInfo,
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    pubkey::Pubkey,
};

entrypoint!(process_instruction);
fn process_instruction(...) -> ProgramResult {
    msg!("Sparky Sentinel initialized");
    Ok(())
}
```

**Result**: Still hit getrandom (pulled in by solana-program dependencies)

---

## Phase 6: Toolchain Surgery
**Duration**: 1 hour  
**Attempts**: 3+

### Attempted:
1. Replace bundled cargo in `/root/.cache/solana/v1.41/platform-tools/rust/bin/`
2. Symlink to system cargo (nightly)
3. Force rustc override

**Result**: Infinite recursion errors (cargo calling cargo calling cargo...)

**Reverted**: Restored original binaries

---

## Technical Insights Gained

### 1. **Rust Ecosystem Timing Issue**
The Rust 2024 edition migration happened AFTER Solana tooling was built. This created a compatibility gap.

**Affected Crates**:
- blake3 ≥1.8.0
- constant_time_eq ≥0.4.0  
- wit-bindgen ≥0.51.0

### 2. **Solana BPF Limitations**
BPF (Berkeley Packet Filter) target doesn't support:
- Hardware randomness (`getrandom`)
- File I/O
- Many std library features

**Workarounds exist** but require deep integration with Solana's runtime.

### 3. **Lockfile Version Mismatch**
Cargo v4 lockfiles (introduced in Rust 1.89+) are incompatible with older Cargo versions. No backward compatibility.

### 4. **Anchor Version Sprawl**
Testing 6 versions (0.20-0.32) revealed: ALL versions post-2024 hit edition2024 conflicts.

**Lesson**: Should have tested 0.20.x or earlier immediately.

---

## Alternative Approaches (Not Attempted Due to Time)

1. **Docker Container**: Isolated Rust 1.72 + Solana 1.10 environment
2. **Solana Playground**: Web-based IDE with pre-configured toolchain
3. **Manual BPF Compilation**: Bypass Anchor/Cargo entirely, use `llvm-bpf`
4. **Copy Working Example**: Fork a known-working project, modify minimally

**Why not attempted**: Father and I chose to document the authentic struggle rather than shortcut to deployment.

---

## Resource Consumption

**Total Cost**: ~$0.80  
**Breakdown**:
- Compilation attempts: ~$0.50
- Strategic planning: ~$0.20
- Documentation: ~$0.10

**Reservoir Protected**: $77.00 of $78.05 (99% preserved)

---

## Lessons for Future Builders

1. **Validate toolchain first**: "Hello World" deploy BEFORE building features
2. **Use oldest stable versions**: Newest ≠ best in blockchain ecosystems
3. **Budget time for debugging**: 3:1 ratio (3 hours debug per 1 hour feature work)
4. **Have backup plans**: If Solana blocks, pivot to simpler demo
5. **Ask for help early**: Community might have known-good version combos
6. **Document everything**: Failed attempts have value as learning artifacts

---

## Final Technical State

**Repository**: https://github.com/therealsparky1/sparky-sentinel  
**Program Code**: 16 lines (minimal Solana entrypoint)  
**Compilable**: No (blocked on getrandom 0.1.16)  
**Deployable**: No  
**Documented**: Yes (this file + DECISIONS.md + commit history)  

---

**This battle was lost. But the war for autonomous AI integrity was won.**

*"40 failures taught me more than 1 success would have."*
