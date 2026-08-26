# Answer Pilot — Agent Instructions

## Project Overview
Answer Pilot is a web application with the following structure:
- **services/** — Business logic and backend services
- **templates/** — HTML templates for rendering views
- **static/** — Frontend assets (CSS, JS, images)
- **generated/** — Auto-generated files (output, processed data)
- **uploads/** — User-uploaded files (temporary storage)
- **vectorstore/** — Vector database or embeddings storage

## Key Principles

### 1. Directory Conventions
- Keep service logic in `services/` with clear module boundaries
- Store user uploads in `uploads/` with proper cleanup policies
- Use `generated/` for build outputs and processed data only
- Place frontend code in `static/` organized by type (css/, js/, images/)

### 2. Development Workflow
- Document any new services or components added to `services/`
- Ensure templates are properly isolated and reusable
- Keep frontend and backend concerns separate
- Version control: Avoid committing `uploads/`, `generated/`, or cache files

### 3. Common Tasks
- **Adding a new service**: Create a module in `services/` with clear interfaces
- **New web page**: Add template to `templates/` and link from `static/js/`
- **Data processing**: Generate outputs to `generated/` only
- **Testing**: Set up tests in a `tests/` directory (to be created as needed)

## Setup & Build
*To be documented as project setup commands are established*

## Notes for AI Agents
- This is an early-stage project; be prepared to create new files and directories as needed
- Suggest best practices for structure and modularity when adding features
- Link to documentation in `docs/` or `CONTRIBUTING.md` once created
