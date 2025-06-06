# Issue Tracker

---

## Issue #1: [Refactor database]
### Description
- Migrate database
- Remove default UUID to BigInterger


## Issue #2: [Move sync to async]
### Description
- Transaction problem: if an error occurs after one transaction commits but before the next completes, the first operation cannot be rolled back.