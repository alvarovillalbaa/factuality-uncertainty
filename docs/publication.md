# Publication status

Last updated: 2026-10-31

Repository: [alvarovillalbaa/factuality-uncertainty](https://github.com/alvarovillalbaa/factuality-uncertainty).
The user created it, and GitHub reports public visibility. Branch:
ai02/offline-verifier, based on a source-linked scope commit on main.
Implementation, pilot, freeze and outcomes are grouped into separate commits.
[Draft PR #1](https://github.com/alvarovillalbaa/factuality-uncertainty/pull/1)
is open and unmerged. Independent annotation is explicitly left pending.

The authenticated GitHub connector successfully read the existing private
decision-runtime repository, but repository-creation capability is absent from
its available tools. Searching for the proposed repository returned no match.
The normal GitHub CLI reported invalid/unavailable authentication and its direct
API call failed connecting to api.github.com. Browser discovery returned no
available browser; documented troubleshooting confirmed an empty browser list.
No credential store was read and no permission boundary was bypassed.

After the user created the repository, connector publication succeeded. Its Git
Data API does not accept original commit authors/timestamps, so remote commit
IDs differ. Every published source tree was checked through its exact Git tree
ID. docs/publication-map.json maps all eight local source commits to their remote
equivalents, including the revision frozen before main outcomes. Original local
commits and result metadata are preserved. Git object IDs use SHA-1;
protocol/payload digests use SHA-256.

The mapped source head is local d80a8a1de18d7fa29c4867a8a6e921c51208ab07
and remote 73f4e5ef7363c5b05f0f84dc9a3f0143d30661bc, with identical trees.
Later documentation commits add this receipt and the final isolated check,
without changing frozen computational inputs or outcomes. No hosted CI or
completed annotation is implied by an open PR. The provisional release remains
distinct from a completed empirical study or product promotion.
