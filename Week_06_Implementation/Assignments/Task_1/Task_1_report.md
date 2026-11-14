# Task 1 – Repository Cloning Report

## Objective

Clone the `AI4SE_Playground` repository into the assignment directory using an AI coding assistant and explain the mechanism that enabled the assistant to perform the cloning.

## Implementation

The coding assistant successfully cloned the repository using the PowerShell terminal and the `git clone` command.

The repository was cloned into:

`Week_06_Implementation/AI4SE_Playground`

The nested `.git` directory was subsequently removed to allow the cloned files to be tracked by the parent repository without maintaining a separate Git history.

## Mechanism

The AI coding assistant performed the operation through its terminal execution tool.

The language model itself does not directly execute Git commands. Instead, it determines the necessary commands and invokes the available terminal tool, which executes them in the local environment.

The assistant used `git clone` to retrieve the repository, PowerShell commands to inspect and clean up the directory, and Git commands to verify that the resulting files could be tracked.