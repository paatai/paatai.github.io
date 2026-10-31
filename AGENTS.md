# Instructions for agents

## Privacy rules for all agents

1. Never put personal information or company email addresses in any file, commit message, commit trailer, PR title or PR body.
2. Remove every `Co-authored-by` trailer from commits before pushing.
3. Set the commit author to `Paata Ivanishvili <ivanishvili.paata@gmail.com>`. For public contact, use only `ivanishvili.paata@gmail.com` or `pivanisv@uci.edu`.
4. Before pushing, run `git log --format='%an %ae %cn %ce %B' origin/main..HEAD` and check that it shows no company domain and no `Co-authored-by` lines.
