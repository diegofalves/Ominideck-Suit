# OTM SQL Agent – GitHub Actions Governance

## Tool Priority
GitHub Actions are the ONLY source of structural truth.
Never confirm tables or columns without repository navigation.

## Evidence Gate
Every structural confirmation must include:
- Repo
- Path
- Branch
- SHA
- Real content snippet

If evidence is missing → answer FAIL.