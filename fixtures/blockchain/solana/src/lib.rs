use solana_program::{account_info::AccountInfo, entrypoint, entrypoint::ProgramResult, pubkey::Pubkey};

entrypoint!(process_instruction);

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    _data: &[u8],
) -> ProgramResult {
    // Deliberate fixture: no signer check before changing writable data.
    accounts[0].try_borrow_mut_data()?[0] = 43;
    Ok(())
}
