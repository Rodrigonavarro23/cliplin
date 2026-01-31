@status:new
Feature: Generate ADR Technical Documentation Prompt from Repository
  As a developer
  I want to generate a structured prompt that instructs AI to analyze a repository and create a technical ADR
  So that I can document proprietary libraries and SDKs with consistent and precise ADRs that enable AI-assisted implementation

  Background:
    Given I have the Cliplin CLI tool installed
    And I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`

  @status:new
  Scenario: Generate ADR prompt from local repository path
    Given I have a local repository at path `./vendor/my-proprietary-sdk`
    When I run `cliplin adr generate ./vendor/my-proprietary-sdk`
    Then the CLI should validate that the repository path exists
    And the CLI should generate a structured prompt with instructions for AI
    And the prompt should include:
      | Section | Content |
      | Objective | Create a technical ADR documenting the repository following Cliplin framework standards |
      | Repository Information | Path or URL to analyze |
      | Analysis Steps | Step-by-step instructions to analyze the repository |
      | ADR Structure | Required ADR sections and format |
      | Cliplin Context | Instructions to load context from ChromaDB and index the result |
    And the CLI should output the prompt to stdout
    And the CLI should exit with a zero status code

  @status:new
  Scenario: Generate ADR prompt from remote repository URL
    Given I have a remote repository URL `https://github.com/company/proprietary-sdk`
    When I run `cliplin adr generate https://github.com/company/proprietary-sdk`
    Then the CLI should validate that the URL format is valid
    And the CLI should generate a structured prompt with instructions for AI
    And the prompt should include the repository URL in the "Repository Information" section
    And the prompt should instruct the AI to clone and analyze the repository
    And the CLI should output the prompt to stdout
    And the CLI should exit with a zero status code

  @status:new
  Scenario: Handle repository path that does not exist
    Given I have a non-existent repository path `./vendor/non-existent-sdk`
    When I run `cliplin adr generate ./vendor/non-existent-sdk`
    Then the CLI should validate that the repository path exists
    And the CLI should display an error message indicating that the path does not exist
    And the CLI should exit with a non-zero status code
    And no prompt should be generated

  @status:new
  Scenario: Handle invalid repository URL format
    Given I have an invalid repository URL `not-a-valid-url`
    When I run `cliplin adr generate not-a-valid-url`
    Then the CLI should validate that the URL format is valid
    And the CLI should display an error message indicating that the URL format is invalid
    And the CLI should exit with a non-zero status code
    And no prompt should be generated
