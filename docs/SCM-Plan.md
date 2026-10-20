# Software Configuration Management (SCM) Plan — COLRS

**Application:** COLRS cafeteria ordering and loyalty-redemption system  
**Selected branching model:** GitHub Flow (`main` + short-lived topic branches)  
**Status:** Project SCM policy

## Purpose

This Software Configuration Management (SCM) Plan defines how changes to COLRS, a cafeteria ordering and loyalty-redemption web application, are identified, versioned, reviewed, tested, released, and recovered. The aim is to keep the application reproducible and demonstrable while protecting the correctness of orders, loyalty-point balances, discounts/redemptions, user access, and stored data. GitHub is the authoritative source for version history, issues, pull requests, and release records.

## Scope

The plan applies to application source code, configuration templates, database schema and migration files, automated tests, documentation, and GitHub workflow files. It also covers deployment configuration for the Railway-hosted application. Secrets, API keys, passwords, real customer/student data, production database dumps, generated build output, and dependency/vendor folders must not be committed. Environment-specific values belong in protected deployment settings or local environment files excluded by .gitignore.

## Roles and Responsibilities

Developer/maintainer (student project owner): creates issues and branches, implements changes, writes or updates tests and documentation, checks the diff, opens pull requests, resolves feedback, maintains releases, and monitors deployment. Reviewer (lecturer, peer, or another developer when available): checks that the change meets acceptance criteria, does not introduce avoidable risks, and includes suitable tests. For a one-person project, the owner performs a documented self-review before merging; an independent review should be requested for security, database, order-total, or loyalty-redemption changes when a reviewer is available. Tester/stakeholder: validates realistic workflows and reports defects with reproducible steps.

## Version Control Strategy

Use Git with GitHub Flow. The default branch is main and should remain in a working, deployable state. Work on one concern per short-lived branch; do not commit directly to main. Use names such as feature/123-order-history, fix/124-redemption-validation, docs/week3-scm-plan, and chore/update-dependencies. Start each branch from an updated main, commit small logical changes with descriptive messages (for example, feat: validate loyalty redemption), and push the branch to GitHub. Open a pull request (PR) targeting main with a summary, linked issue, test evidence, screenshots for UI changes where useful, and migration or rollback notes where relevant. Review the diff and checks before merging; delete the branch after the PR is merged. Avoid long-lived develop/release branches because the project has one main maintainer and relatively infrequent milestone releases.

## Change Control Strategy

Track every bug or non-trivial feature in GitHub Issues with the problem, expected result, acceptance criteria, priority, and affected area. Treat documentation/cosmetic edits as low risk, normal UI/API changes as medium risk, and order totals, point earning/redemption, authentication, schema, or deployment changes as high risk. High-risk changes require explicit boundary/failure tests, review by another person where available, and a rollback/recovery note. Test that a reward cannot be redeemed twice, failed operations do not leave order/points inconsistent, and limits calculate correctly. Record discussion in the PR, never bypass checks for risky changes, and use a reviewed revert plus a known-good deployment to recover. Back up data before schema changes.

## CI/CD Process Control Strategy

Configure GitHub Actions to run on pull requests targeting main and on pushes to main. The workflow should install locked dependencies using the package manager already used by the project, run available lint/static checks and automated tests, and build the application. A failed check must be fixed before merge; enable a required status check on main when the repository settings and available workflow permit it. For UI or business-critical behavior not fully covered by automation, perform and record a manual smoke test. The smoke-test path should include sign-in/role access, placing or managing an order, earning points, and redeeming a reward/discount. Deploy from main to Railway only after validation; if automated deployment is configured, ensure it follows successful checks, otherwise use a controlled manual deployment. Store credentials in Railway/GitHub environment secrets, never in source files or logs. After deployment, verify service health and the core workflow; if it fails, roll back to the last known-good deployment or revert the responsible change.

## Issue Tracking Tool and Workflow

Use GitHub Issues as the system of record, with GitHub Projects or labels to show progress. Suggested labels are type:bug, type:feature, type:documentation, priority:high, priority:normal, and area:orders, area:loyalty, area:auth, or area:deployment. Move work through Backlog → Ready → In progress → In review → Done (using project status fields or agreed labels). The developer creates the branch from an issue, references the issue in the PR, responds to review comments, and closes the issue after merge and verification; use a PR phrase such as Fixes #123 when the change fully resolves that issue. Bug reports should include steps to reproduce, expected versus actual behavior, environment, and screenshots/logs with secrets or personal data removed.

## Release Strategy

Treat COLRS as a pre-1.0 academic prototype and use semantic-version-style tags: 0.minor.patch. Increment the patch number for a backward-compatible bug fix (for example, v0.1.1) and the minor number for a new feature or milestone (for example, v0.2.0). Reserve v1.0.0 for a release considered stable enough for its intended use. Create a Git tag and GitHub Release from a validated main commit. Release notes should summarize features, fixes, known limitations, database/configuration changes, and any manual deployment steps. Before a demonstration or release, confirm that checks pass and complete the core smoke test. Back up relevant data before schema changes and record the deployed version/commit so the previous working build can be restored.

## References

- [Kubernetes CONTRIBUTING.md](https://github.com/kubernetes/kubernetes/blob/master/CONTRIBUTING.md)
- [Kubernetes contributor guide](https://www.kubernetes.dev/docs/guide/contributing/)
- [Kubernetes pull request process](https://www.kubernetes.dev/docs/guide/pull-requests/)
- [Kubernetes contributor cheatsheet (branch strategy)](https://www.kubernetes.dev/docs/contributor-cheatsheet/)
- [GitHub Flow documentation](https://docs.github.com/en/get-started/using-github/github-flow)
