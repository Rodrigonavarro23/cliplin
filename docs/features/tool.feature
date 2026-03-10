@constraints
# governed_by:
#   - docs/tdrs/cliplin-cli-stack.md
#   - docs/tdrs/system-modules.md
# conflicts: []
# gaps:
#   - "No spec for webview library selection or minimum version requirement"
#   - "No spec for cross-platform webview behavior differences (macOS vs Windows vs Linux)"
#   - "No spec for what happens when the webview opens but the HTML file fails to load internally"
Feature: Tool Command
  As a developer
  I want to open tools from the CLI
  So that I can use single page applications (SPAs) provided by Cliplin

  Background:
    Given I have the Cliplin CLI tool installed
    And Cliplin has a `tools/` directory in its package directory
    And Cliplin has a `tools/tools.yaml` configuration file that maps tool names to their files

  @status:implemented
  @changed:2024-01-15
  Scenario: Open a tool by name
    Given Cliplin has a tool named "ui-intent" configured in its package `tools/tools.yaml`
    And the tool "ui-intent" maps to a file "ui-intent.html" in Cliplin's `tools/` directory
    When I run `cliplin tool ui-intent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should find the tool "ui-intent" in the configuration
    And the CLI should locate the file "ui-intent.html" in Cliplin's `tools/` directory
    And the CLI should open a webview window
    And the webview should load the SPA from Cliplin's tools directory
    And the webview window should display the tool interface

  @status:implemented
  @changed:2024-01-15
  Scenario: List available tools
    Given Cliplin has multiple tools configured in its package `tools/tools.yaml`
    When I run `cliplin tool --list` or `cliplin tool list`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should display a list of all available tools
    And the CLI should show the tool name and associated file for each tool
    And the CLI should exit successfully

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle tool not found
    Given Cliplin has a `tools/tools.yaml` configuration file in its package
    And the tool "non-existent" is not configured in Cliplin's tools
    When I run `cliplin tool non-existent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should display an error message indicating that the tool "non-existent" was not found
    And the CLI should list available tools
    And the CLI should exit with a non-zero status code
    And no webview should be opened

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle missing tools directory
    Given Cliplin is installed
    And Cliplin's `tools/` directory does not exist in the package
    When I run `cliplin tool ui-intent`
    Then the CLI should detect that Cliplin's `tools/` directory does not exist
    And the CLI should display an error message indicating that the Cliplin tools directory is missing
    And the CLI should suggest that this is a Cliplin installation issue
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle missing tools configuration file
    Given Cliplin is installed
    And Cliplin's `tools/` directory exists in the package
    And Cliplin's `tools/tools.yaml` file does not exist
    When I run `cliplin tool ui-intent`
    Then the CLI should detect that Cliplin's `tools/tools.yaml` file does not exist
    And the CLI should display an error message indicating that the configuration file is missing
    And the CLI should suggest that this is a Cliplin installation issue
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle missing tool file
    Given Cliplin has a tool named "ui-intent" configured in its package `tools/tools.yaml`
    And the tool "ui-intent" maps to a file "ui-intent.html"
    And the file "ui-intent.html" does not exist in Cliplin's tools directory
    When I run `cliplin tool ui-intent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should find the tool "ui-intent" in the configuration
    And the CLI should detect that the file does not exist in Cliplin's tools directory
    And the CLI should display an error message indicating that the tool file is missing
    And the CLI should exit with a non-zero status code
    And no webview should be opened

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle invalid tools configuration file
    Given Cliplin is installed
    And Cliplin's `tools/` directory exists in the package
    And Cliplin's `tools/tools.yaml` file exists but contains invalid YAML
    When I run `cliplin tool ui-intent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should attempt to read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should detect that the YAML is invalid
    And the CLI should display an error message indicating that the configuration file is invalid
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Open tool with absolute file path
    Given Cliplin has a tool named "custom-tool" configured in its package `tools/tools.yaml`
    And the tool "custom-tool" maps to an absolute file path "/path/to/tool.html"
    When I run `cliplin tool custom-tool`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should find the tool "custom-tool" in the configuration
    And the CLI should resolve the absolute path
    And the CLI should verify that the file exists
    And the CLI should open a webview with the tool loaded from the absolute path

  @status:implemented
  @changed:2024-01-15
  Scenario: Open tool with relative file path
    Given Cliplin has a tool named "ui-intent" configured in its package `tools/tools.yaml`
    And the tool "ui-intent" maps to a relative file path "ui-intent/index.html"
    When I run `cliplin tool ui-intent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should read the configuration from Cliplin's `tools/tools.yaml`
    And the CLI should find the tool "ui-intent" in the configuration
    And the CLI should resolve the relative path from Cliplin's `tools/` directory
    And the CLI should verify that the file exists in Cliplin's tools directory
    And the CLI should open a webview with the tool loaded from the resolved path

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle webview errors gracefully
    Given Cliplin has a tool named "ui-intent" configured in its package `tools/tools.yaml`
    And the tool "ui-intent" maps to a valid file "ui-intent.html" in Cliplin's tools directory
    And the webview library fails to initialize
    When I run `cliplin tool ui-intent`
    Then the CLI should locate Cliplin's tools directory from the package installation
    And the CLI should attempt to open the webview
    And if the webview fails to initialize, the CLI should display an error message
    And the CLI should suggest checking webview dependencies
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Tools configuration file structure
    Given Cliplin has a `tools/tools.yaml` configuration file in its package
    Then the configuration file should have a valid YAML structure
    And the configuration should map tool names to file paths
    And the configuration structure should be:
      | Field | Type | Description |
      | tools | object | Map of tool names to file paths |
      | tools.<name> | string | File path (relative to Cliplin's tools/ or absolute) |
    And example configuration should be:
      ```yaml
      tools:
        ui-intent: ui-intent.html
        another-tool: subdirectory/tool.html
      ```
    And the tools directory and configuration are part of the Cliplin package, not user projects

