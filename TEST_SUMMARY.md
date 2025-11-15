# Unit Tests for Save Operation and Redirects

## Summary

Unit tests have been successfully added to verify save operation redirect behavior for both Login and Register components. All tests are passing (29 total tests across both files).

## Test Cases Added

### Login Component (`src/tests/views/Login.test.js`)

Added 6 new test cases in the "Login - Save Operation and Redirects" describe block:

1. **should correctly redirect the user after a successful login**
   - Verifies that `router.push()` is called when login succeeds
   - Ensures basic redirect functionality works

2. **should redirect to the correct page after a successful login (main page)**
   - Tests default redirect behavior (no query parameters)
   - Verifies redirect to `{ name: 'main' }`

3. **should redirect to the saved tab after successful login when redirect=saved query param is present**
   - Tests redirect with query parameter `redirect=saved`
   - Verifies redirect to `{ name: 'main', query: { tab: 'saved' } }`

4. **should redirect to pending save page after successful login when redirect=pending-save query param is present**
   - Tests redirect with query parameter `redirect=pending-save`
   - Verifies redirect to `{ name: 'main', query: { restored: 'pending' } }`

5. **should not redirect and display an error when login fails due to invalid credentials**
   - Tests failed login scenario with invalid credentials
   - Verifies that `router.push()` is NOT called
   - Confirms error message is displayed: "Invalid email or password"
   - Checks that error element exists in DOM

6. **should display a generic error message when login fails without a specific message**
   - Tests failed login without specific error message
   - Verifies that `router.push()` is NOT called
   - Confirms generic error message: "Login failed"

### Register Component (`src/tests/views/Register.test.js`)

Added 7 new test cases in the "Register - Save Operation and Redirects" describe block:

1. **should correctly redirect the user after a successful registration**
   - Verifies that `router.push()` is called when registration succeeds
   - Ensures basic redirect functionality works

2. **should redirect to the correct page after a successful registration (main page)**
   - Tests default redirect behavior (no query parameters)
   - Verifies redirect to `{ name: 'main' }`

3. **should redirect to the saved tab after successful registration when redirect=saved query param is present**
   - Tests redirect with query parameter `redirect=saved`
   - Verifies redirect to `{ name: 'main', query: { tab: 'saved' } }`

4. **should redirect to pending save page after successful registration when redirect=pending-save query param is present**
   - Tests redirect with query parameter `redirect=pending-save`
   - Verifies redirect to `{ name: 'main', query: { restored: 'pending' } }`

5. **should not redirect and display an error when registration fails due to invalid data**
   - Tests failed registration scenario (e.g., email already exists)
   - Verifies that `router.push()` is NOT called
   - Confirms error message is displayed: "Email already exists"
   - Checks that error element exists in DOM

6. **should display a generic error message when registration fails without a specific message**
   - Tests failed registration without specific error message
   - Verifies that `router.push()` is NOT called
   - Confirms generic error message: "Registration failed"

7. **should not redirect when registration fails with weak password error**
   - Tests failed registration due to weak password
   - Verifies that `router.push()` is NOT called
   - Confirms error message: "Password must be at least 8 characters long"
   - Checks that error element exists in DOM

## Coverage

These tests cover the three main scenarios requested:

1. ✅ **Verify that a successful save operation correctly redirects the user**
   - Covered by tests #1, #2, #3, #4 in both Login and Register

2. ✅ **Verify that the user is redirected to the correct page after a successful save**
   - Covered by tests #2, #3, #4 in both Login and Register
   - Tests verify different redirect destinations based on query parameters

3. ✅ **Verify that no redirect occurs and an error is displayed when a save operation fails due to invalid data**
   - Covered by tests #5, #6, #7 in both Login and Register
   - Tests verify error messages are displayed and no redirect occurs

## Test Results

```
Test Files  2 passed (2)
     Tests  29 passed (29)
  Duration  724ms
```

All tests are passing successfully.

## Technical Implementation

- Uses Vitest as the testing framework
- Uses Vue Test Utils for component mounting and testing
- Mocks `useAuth`, `useRouter`, and `useRoute` composables
- Tests both success and failure scenarios
- Verifies router navigation behavior
- Checks DOM for error message display
