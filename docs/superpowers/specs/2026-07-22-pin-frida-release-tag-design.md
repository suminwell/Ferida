# Pin Ferida Builds to the Frida Release Tag

## Goal

Ensure each Ferida GitHub Release is built from the exact Frida tag used as
its version, instead of from Frida's default branch at workflow runtime.

## Scope

Only `ferida/.github/workflows/build.yml` will change. The `android-core`
workflow and its intentionally independent release lifecycle remain unchanged.

## Design

The Android build job will expose the version produced by `check_version` as
`FRIDA_VERSION`. It will clone Frida with `--branch "$FRIDA_VERSION"` and
`--recurse-submodules`, so the superproject and its submodules start from the
release-selected source tree.

Immediately after cloning, the workflow will compare the checked-out `HEAD`
with the commit referenced by `refs/tags/$FRIDA_VERSION`. A missing tag or a
mismatch will stop the job before any patches are applied.

The existing Ferida patch loop and four-ABI Android build remain unchanged.
Patch incompatibility with a new Frida release is expected to fail at
`git am`; adapting such patches remains a deliberate manual task.

## Error Handling

- Missing Frida release tag: `git clone --branch` fails.
- Checked-out commit does not match the tag: the explicit verification fails.
- Ferida patch conflicts with the new Frida source: `git am` fails.
- No failure in this workflow triggers an `android-core` release.

## Verification

Because this is a workflow-only configuration change, verification will use:

1. A shell assertion that fails before the change because the clone command
   does not select `FRIDA_VERSION`.
2. The same assertion passing after the change.
3. YAML parsing of the updated workflow.
4. A diff review confirming that no `android-core` files or unrelated Ferida
   behavior changed.
