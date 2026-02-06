use anchor_lang::prelude::*;

declare_id!("3zxmH7fvqSUzefogvU1JMRNR1vPhQhdZgAvwerrSqZBp");

#[program]
pub mod sparky_sentinel {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("Greetings from: {:?}", ctx.program_id);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}
