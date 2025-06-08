# Issue Tracker

---

## Issue #1: [Refactor database]
### Description
- Migrate database
- Remove default UUID to BigInterger


## Issue #2: [Move sync to async]
### Description
- **Transaction problem**: if an error occurs after one transaction commits but before the next completes, the first operation cannot be rolled back.
- **Solution**: There is not yet an optimal solution

## Issue #3: [Race-condition]
### Description:
- **Problem**: When multiple requests concurrently check for a resource's existence (SELECT) and then write it (INSERT), 
a later request might act on stale data, causing a UNIQUE constraint violation. This is a Race Condition.
- **Solution**: Skip the pre-check (SELECT). Instead, directly attempt the write operation (INSERT) 
and be prepared to "ask for forgiveness" (handle the error) if it fails. 
This is the EAFP (Easier to Ask for Forgiveness than Permission) principle.
```cmd
async def create(self, instance):
    self.session.add(instance)
    try:
        await self.session.commit()  # Just try to write; the DB is the referee
        await self.session.refresh(instance)
        return instance
    except IntegrityError:  # If the database raises an error (e.g., duplicate)
        await self.session.rollback()  # Step 1: Clean up (rollback)
        raise DuplicateEntryError(...)
```