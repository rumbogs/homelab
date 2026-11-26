# Branch ruleset for main, as code. jq builds the JSON body for the
# GitHub rulesets API (jq allows comments; JSON doesn't). Apply with:
#   jq -n -f .github/rulesets/main.jq |
#     gh api -X POST 'repos/{owner}/{repo}/rulesets' --input -
# LEARN [CI]: a ruleset is GitHub's newer branch protection. Settings live
# here in git, so a change to them is reviewed like any other change.
{
  name: "main",
  target: "branch",
  # TODO(you) [CI]: one of "active", "evaluate" or "disabled". "evaluate"
  # only logs what would be blocked, and needs GitHub Enterprise.
  enforcement: "active",
  # LEARN [SEC]: an empty bypass list means nobody skips the rules, not
  # even the repo owner. Any bypass is a hole a stolen token could use.
  bypass_actors: [],
  conditions: {
    ref_name: {
      # TODO(you) [CI]: which branches the rules cover. Either a ref like
      # "refs/heads/main", or the alias "~DEFAULT_BRANCH", which follows a
      # rename of the default branch. Either works; say why you chose it.
      include: ["refs/heads/main"],
      exclude: []
    }
  },
  rules: [
    # Nobody can delete main.
    { type: "deletion" },
    # TODO(you) [SEC]: the rule type that blocks force-pushes. A plain
    # push only moves the branch forward ("fast-forward"); what does git
    # call a push that doesn't? The type is that name in snake_case.
    { type: "non_fast_forward" },
    {
      type: "pull_request",
      parameters: {
        # TODO(you) [CI]: approvals needed before merge. You are the only
        # person on the repo and GitHub won't let you approve your own PR.
        required_approving_review_count: 0,
        dismiss_stale_reviews_on_push: false,
        require_code_owner_review: false,
        require_last_push_approval: false,
        required_review_thread_resolution: false,
        allowed_merge_methods: ["squash"]
      }
    },
    {
      type: "required_status_checks",
      parameters: {
        # LEARN [CI]: strict means the branch must be up to date with main
        # before merge, so checks ran against the code that will land.
        strict_required_status_checks_policy: true,
        # LEARN [SEC]: integration_id pins a check to the app that must
        # report it (15368 is GitHub Actions). Without it, anyone with
        # write access could post a fake green "secrets" status via the API.
        required_status_checks: [
          # TODO(you) [SEC]: the check that blocks a leaked secret. A
          # context is the job's name as `gh pr checks` lists it.
          { context: "secrets", integration_id: 15368 },
          # TODO(you) [CI]: the check that lints and tests the harness.
          { context: "harness", integration_id: 15368 }
        ]
      }
    }
  ]
}
