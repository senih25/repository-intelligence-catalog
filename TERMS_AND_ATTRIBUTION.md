# Terms and Attribution

This project uses public repository metadata retrieved from GitHub interfaces.

## Source boundary
- Repository metadata remains attributable to GitHub and the respective repository owners.
- This project does not claim ownership of third-party repository source code, descriptions, names, trademarks, or licenses.
- A public repository is not automatically reusable open-source software; license review is required before reuse.
- The public product package must not be used to sell or expose GitHub users' personal information.

## GitHub API use
GitHub API use is subject to the GitHub Terms of Service and API Terms. The current product architecture intentionally uses:
- query-first retrieval,
- bounded metadata snapshots,
- live enrichment only for shortlisted repositories,
- no token-sharing to bypass rate limits,
- no repository source-code mirroring.

Current terms reference:
https://docs.github.com/en/site-policy/github-terms/github-terms-of-service

## Dataset publication
Any future public dataset release must:
1. state retrieval date and source;
2. include only fields approved by the release schema;
3. exclude secrets/private data;
4. preserve third-party rights notices;
5. avoid implying endorsement by GitHub or repository owners;
6. use a separately approved dataset/compilation license or rights notice.

## Commercialization boundary
The product is positioned as a repository decision-intelligence workflow and derived analysis layer, not as resale of GitHub itself or a bulk mirror of GitHub content.
