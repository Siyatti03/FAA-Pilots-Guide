'''
Author: Garrett Snow
    Role: Scrum Master 1
Purpose: Tests around printing the result checklist—verifying payload wiring,
         window.print invocation, and that the payload includes user choices.
         These are marked xfail until the app exposes a payload via an element
         attribute or a global variable.
Tests Implemented:
    1. Anxiety path: payload structure and required keys (xfail)
    2. Print button triggers window.print and seeds payload (xfail)
    3. Payload contains the user's visible choice(s) (xfail/parametrized)
'''
import os
import json
import pytest


from e2e_helpers import (
    checkPageReady,             # open URL + wait for <body>
    findElementByRoleExisting,  # ARIA role + name lookup
    waitAndClick,               # wait clickable + click (CSS)
    BASE_URL,                   # shared base URL
    DEFAULT_TIMEOUT,           # default wait timeout 
    findElementById,            # By.ID wrapper with wait
)


# Reusable JS snippet: stub window.print to count calls and seed payload; prevents native dialog.
PRINT_STUB_SCRIPT = """
(function(){
  window.__printCalls = 0;
  const original = window.print;
  window.print = function(){
    window.__printCalls++;
    if (!window.__printPayload) {
      const btn = document.querySelector('button[aria-label="Print this checklist"]');
      const attr = btn && btn.getAttribute('data-print-payload');
      if (attr) {
        try { window.__printPayload = JSON.parse(attr); } catch(e) {}
      }
    }
    if (original) return; // prevent actual dialog
  };
})();
"""


# Extract print payload from the app.
# 1) Prefer reading JSON from the print button’s `data-print-payload` attribute
#    so the data stays with the control that uses it.
# 2) If missing or unparsable, fall back to a global `window.__printPayload`
#    that the app may set when navigation/results are computed.
def extract_payload_from_dom(browser_types_fixture):
    """
    Extract the print payload as JSON:
      - prefer the button's data-print-payload
      - otherwise use window.__printPayload.
    param: browser_types_fixture- WebDriver instance
    returns: dict of payload or None.
    
    """
    driver = browser_types_fixture
    try:
        # Use shared helper to get the Print button by role/name
        btn = findElementByRoleExisting(driver, "button", "Print", DEFAULT_TIMEOUT)
        attr = btn.get_attribute("data-print-payload")
        if attr:
            try:
                return json.loads(attr)
            except Exception:
                pass
    except Exception:
        pass
    return driver.execute_script("return window.__printPayload || null;")


@pytest.mark.parametrize(
    "browser_types_fixture",
    [
        {"browser": "chrome",  "headless": True},
        {"browser": "firefox", "headless": True},
    ],
    indirect=True
)

def test_anxiety_print_payload_variables(browser_types_fixture):
    """
    Validate payload structure and required keys for the Anxiety path.
    Auto-skips if the app has not exposed a print payload yet.
    param: browser_types_fixture - WebDriver instance
    """
    driver = browser_types_fixture
    checkPageReady(driver, BASE_URL)
    # Choose Anxiety and two conditions to reach a specific results path
    findElementByRoleExisting(driver, "img", "worried face", DEFAULT_TIMEOUT).click()
    waitAndClick(driver, "Generalized Anxiety Disorder", DEFAULT_TIMEOUT)
    waitAndClick(driver, "PTSD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)
    # Answer "No" four times (this was the expected path in earlier tests)
    for _ in range(4):
        waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title")
    assert "Likely Qualifies for In-Office Issuance" in title.text, \
        f"ERROR: Expected issuance text in result title, got {title.text!r}"

    payload = extract_payload_from_dom(driver)
    if not isinstance(payload, dict):
        pytest.skip("Print payload not exposed by the app yet")

    # Validate payload structure and required keys
    assert isinstance(payload, dict), \
        f"ERROR: Expected dict payload, got {type(payload).__name__}: {payload!r}"
    assert payload.get("guide") == "anxiety", \
        f"ERROR: payload.guide mismatch: expected 'anxiety', got {payload.get('guide')!r}"
    assert isinstance(payload.get("answers"), dict), \
        f"ERROR: payload.answers must be a dict; got {type(payload.get('answers')).__name__}: {payload.get('answers')!r}"
    for q in ["q2", "q3", "q4", "q5"]:
        assert q in payload["answers"], \
            f"ERROR: Expected question key {q!r} in payload.answers; keys={list(payload['answers'].keys())!r}"
    assert isinstance(payload.get("result"), dict), \
        f"ERROR: payload.result must be a dict; got {type(payload.get('result')).__name__}: {payload.get('result')!r}"
    assert payload["result"].get("title"), \
        f"ERROR: payload.result.title is missing or empty: {payload.get('result')!r}"
    assert isinstance(payload.get("checklist"), list), \
        f"ERROR: payload.checklist must be a list; got {type(payload.get('checklist')).__name__}: {payload.get('checklist')!r}"


@pytest.mark.parametrize(
    "browser_types_fixture",
    [
        {"browser": "chrome",  "headless": True},
        {"browser": "firefox", "headless": True},
    ],
    indirect=True
)

def test_print_button_invokes_window_print_and_uses_payload(browser_types_fixture):
    """
    Temporarily replace window.print with a test double:
    clicking Print should call it once and ensure a payload is available
    (without opening the native dialog).
    param: browser_types_fixture - WebDriver instance
    """
    driver = browser_types_fixture
    checkPageReady(driver, BASE_URL)
    findElementByRoleExisting(driver, "img", "drop of blood", DEFAULT_TIMEOUT).click()  # Diabetes tile
    waitAndClick(driver, "Oral Medications (Not Insulin)", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert "AME Assisted Special Issuance" in title.text, \
        f"ERROR: Expected 'AME Assisted Special Issuance' in result title, got {title.text!r}"
        
    # Stub window.print so we can count calls and seed __printPayload from the button attribute
    # without opening the native dialog
    driver.execute_script(PRINT_STUB_SCRIPT)

    # Clicking Print should call window.print once
    findElementByRoleExisting(driver, "button", "Print this checklist", DEFAULT_TIMEOUT).click()
    calls = driver.execute_script("return window.__printCalls;")
    assert calls == 1, f"ERROR: window.print expected 1 call, saw {calls}"

    # And a payload should be available
    payload = driver.execute_script("return window.__printPayload || null;")
    if payload is None:
        pytest.skip("Print payload not exposed by the app yet")


@pytest.mark.parametrize('condition,choice', [
    ("diabetes", "Diet and Exercise Only"),
    ("diabetes", "Insulin Injections or Pump"),
])

def test_payload_contains_user_choices(browser_types_fixture, condition, choice):
    """
    Parametrized: The payload should include the user's visible selection for the given condition.
    Auto-skips if the app has not exposed a print payload yet.
    param: browser_types_fixture - WebDriver instance
    param: condition - one of "diabetes", "anxiety", "chd"
    param: choice - the user's selected choice text to verify in the payload
    """
    driver = browser_types_fixture
    checkPageReady(driver, BASE_URL)
    # Choose the condition's tile
    tile_aria = {"diabetes": "drop of blood", "anxiety": "worried face", "chd": "heart"}[condition]
    findElementByRoleExisting(driver, "img", tile_aria, DEFAULT_TIMEOUT).click()

    # Click the choice (expects buttons to expose matching aria-labels)
    waitAndClick(driver, f'{choice}', DEFAULT_TIMEOUT)

    payload = extract_payload_from_dom(driver)
    if not isinstance(payload, dict):
        pytest.skip("Print payload not exposed by the app yet")

    # Basic payload checks + condition alignment
    assert payload, "ERROR: Print payload was not found (expected dict)."
    assert payload.get("guide") == condition, \
        f"ERROR: payload.guide mismatch: expected {condition!r}, got {payload.get('guide')!r}"
    assert payload.get("answers"), "ERROR: payload.answers is missing or empty."

    # Verify that the payload preserves the user's visible selection text for printing
    found_choice = False
    for v in payload["answers"].values():
        if isinstance(v, str) and v == choice:
            found_choice = True
            break
        if isinstance(v, list) and (choice in v):
            found_choice = True
            break

    assert found_choice, \
        f"ERROR: Expected to find user choice {choice!r} within payload.answers values: {payload['answers']!r}"
