# NetFort --- Web Firewall Simulator Implementation Plan

> **Purpose:** Convert the existing NetFort desktop firewall simulator
> into a polished, browser-based educational demo that runs the same
> synthetic packet stream through a packet-filtering firewall and a
> stateful-inspection firewall, animates decisions clearly, and explains
> the metric differences.
>
> **Design direction:** Simple, sleek, neutral, minimal, and
> presentation-ready. The provided palette is the visual foundation. Use
> bright red and green only to communicate blocked/rejected and
> accepted/allowed packet outcomes. The Metrics page is the one
> deliberate exception to the restrained palette: it may use a broader
> set of vivid, accessible data-visualization colors.

------------------------------------------------------------------------

## 1. Product goals and demo story

The website should let a presenter explain the firewall process from
beginning to end without needing to explain the interface itself.

A visitor should be able to:

1.  Open a dashboard and understand what the simulator does.
2.  Select a prepared traffic scenario or use a curated default
    scenario.
3.  Start a **slow, step-by-step simulation** and watch each packet move
    through the firewall engine.
4.  See the decision for every packet, including the exact rule or
    stateful connection that caused the result.
5.  Open the rule editor, change a rule, and rerun the same traffic to
    show how policy changes affect outcomes.
6.  Open a comparison page, run both firewall models against the **same
    packet stream**, and compare outcomes and performance metrics.
7.  Open a Metrics page that explains every metric in plain language and
    makes differences easy to present.
8.  Reset the demo to a known state.

The simulator is educational. It must operate only on generated or
explicitly supplied simulation packets. It must **not** capture real
traffic, change the host firewall, create operating-system firewall
rules, or send packets to real network destinations.

### Core demo narrative

**Traffic source → packet stream → firewall engine → decision and reason
→ outcome metrics.**

For the comparison experience, fork the same immutable packet stream
into two independent simulations:

-   **Packet-filtering firewall:** evaluates each packet against ordered
    rules without remembering connection history.
-   **Stateful-inspection firewall:** checks whether a packet belongs to
    an established tracked connection, then applies the ordered rules to
    packets that are not recognized as part of an existing connection.

Make the difference visible through scenarios containing replies to
allowed connections, unsolicited inbound packets, blocked connection
attempts, rule-order conflicts, and traffic that should be rejected by
policy.

------------------------------------------------------------------------

## 2. Design system

### 2.1 Main palette

Use the following palette from the supplied reference image.

  ------------------------------------------------------------------------
  Token                    Hex                     Intended use
  ------------------------ ----------------------- -----------------------
  `--color-peach`          `#FFDBBB`               Warm accent surface,
                                                   selected navigation
                                                   background, subtle
                                                   highlights

  `--color-stone`          `#CCBEB1`               Secondary surfaces,
                                                   borders, dividers,
                                                   inactive controls

  `--color-taupe`          `#997E67`               Muted accent, secondary
                                                   buttons, chart neutral
                                                   series, icons

  `--color-brown`          `#664930`               Primary brand color,
                                                   headings, primary
                                                   buttons, sidebar
                                                   details

  `--color-canvas`         `#FAF8F5`               Main page background;
                                                   warm off-white

  `--color-surface`        `#FFFFFF`               Cards, panels, menus,
                                                   tables

  `--color-text`           `#26221F`               Main text

  `--color-text-muted`     `#75685D`               Supporting text and
                                                   descriptions

  `--color-border`         `#E6DDD4`               Hairline borders and
                                                   separators

  `--color-allowed`        `#16A34A`               **Allowed/accepted
                                                   packets only**

  `--color-blocked`        `#DC2626`               **Blocked/rejected
                                                   packets only**

  `--color-allowed-soft`   `#DCFCE7`               Pale backgrounds for
                                                   allowed status labels

  `--color-blocked-soft`   `#FEE2E2`               Pale backgrounds for
                                                   blocked status labels
  ------------------------------------------------------------------------

The green and red are reserved for packet outcomes and directly related
outcome indicators. Do not use green/red as generic brand colors,
decorative gradients, navigation colors, or unrelated status colors.

For text and icons on the neutral palette, check contrast. Use dark
brown or near-black on peach and stone surfaces. Use white on the dark
brown primary button only when the resulting contrast is sufficient.

### 2.2 Visual style

-   Minimal surfaces, clear spacing, and restrained borders.
-   Prefer subtle 1 px borders over heavy shadows.
-   Use small corner radii consistently: approximately 8--12 px for
    cards and 6--8 px for controls.
-   Use a spacing scale based on 4 px: 4, 8, 12, 16, 24, 32, 40, 48.
-   Avoid glassmorphism, neon cyberpunk effects, glowing borders,
    excessive gradients, and decorative network graphics that compete
    with the packet flow.
-   Use one clean sans-serif family, such as Inter or a system
    sans-serif fallback.
-   Use tabular numerals for metrics, packet counts, IP addresses,
    ports, and timestamps.
-   Animate with restrained transitions. Packet movement should be
    meaningful, not ornamental.
-   Provide a clear focus ring, hover state, disabled state, and
    keyboard-operable controls.
-   Never rely on color alone: pair green/red with **ALLOW/BLOCK** text
    and an icon.

### 2.3 Outcome iconography

Use a consistent icon set such as Lucide:

-   Allowed: `CheckCircle2` or `ShieldCheck`, green, with `ALLOWED`.
-   Blocked: `XCircle` or `ShieldX`, red, with `BLOCKED`.
-   Pending/in transit: `CircleDashed` or `ArrowRight`, taupe/brown.
-   Rule: `ListFilter` or `SlidersHorizontal`.
-   Dashboard: `LayoutDashboard`.
-   Live simulation: `Activity` or `Play`.
-   Comparison: `GitCompareArrows`.
-   Metrics: `ChartNoAxesCombined` or `ChartColumnIncreasing`.
-   Packet log: `ScrollText`.
-   Settings/help: `Settings2`, `CircleHelp`.
-   Reset: `RotateCcw`.
-   Pause: `Pause`.
-   Stop: `Square`.
-   Resume: `Play`.
-   Expand details: `ChevronDown`.

Use the same icon family and stroke weight throughout.

------------------------------------------------------------------------

## 3. Application shell and navigation

### 3.1 Desktop layout

Use a fixed-width vertical sidebar on the **left** and a flexible main
content area on the right.

-   Sidebar width: about 232 px when expanded.
-   Optional collapsed width: about 72 px, but do not make collapse a
    required MVP feature.
-   Main content max width: about 1440 px; center it on very wide
    screens.
-   Header height: about 72 px.
-   Main content padding: 28--36 px on desktop, 20--24 px on tablet, 16
    px on mobile.
-   Main background: `--color-canvas`.
-   Cards: white surfaces with neutral borders.

Sidebar structure:

1.  **Brand block:** small shield/network icon and `NetFort`.
2.  **Navigation, vertically stacked:**
    -   Dashboard --- `LayoutDashboard`
    -   Live Simulation --- `Activity`
    -   Compare Firewalls --- `GitCompareArrows`
    -   Rules --- `ListFilter`
    -   Metrics --- `ChartNoAxesCombined`
    -   Packet Log --- `ScrollText`
3.  **Bottom block:** `Demo Mode` label and a small "Synthetic traffic
    only" note, plus Help/About if needed.

Each item must have an icon on the left and a concise text label. The
selected page uses a peach-tinted background and dark-brown text/icon.
Unselected items use muted text and a subtle hover surface. Do not use
red or green to highlight navigation.

On smaller screens, turn the sidebar into a drawer opened by a menu
button; preserve the same page order and icons. Do not simply shrink the
desktop sidebar until labels become unreadable.

### 3.2 Top header

The header is intentionally quiet:

-   Left: page title and optional one-line subtitle.
-   Right: scenario selector or scenario badge where relevant,
    simulation status, and a `Reset demo` control.
-   Avoid a large hero banner on every page.
-   Display a small `SIMULATION ONLY` label in neutral colors so the
    safe, simulated nature of the product is clear.

### 3.3 Shared interaction rules

-   Keep the same page title placement, card styles, buttons, tables,
    tooltips, and status labels across all pages.
-   Primary action buttons use dark brown with white text.
-   Secondary actions use white/transparent surfaces with a neutral
    border.
-   Destructive actions use a neutral confirmation dialog; red is
    reserved for the destructive/outcome meaning, not decoration.
-   Confirm before deleting a rule or resetting customized rules.
-   While a simulation is running, prevent changes that would mutate its
    active traffic or rules. Either disable the relevant editor or
    require the user to stop and restart.
-   Every simulation run gets a run ID and records which
    rules/configuration it used. Show this in run details so a presenter
    can explain reproducibility.

------------------------------------------------------------------------

## 4. Page-by-page layout

## 4.1 Dashboard

**Purpose:** Provide a quick overview and a clear starting point for the
demo.

### Layout

**Page heading** - Title: `Firewall Lab` - Subtitle:
`Explore how packet filtering and stateful inspection handle the same traffic.` -
Main CTA: `Start a simulation` - Secondary CTA: `Compare firewalls`

**Top row --- four compact summary cards** 1. Packets in latest run. 2.
Allowed packets. 3. Blocked packets. 4. Active tracked connections
(stateful model).

Use neutral card surfaces. Green/red may appear only on the
allowed/blocked values and their outcome icons.

**Middle section --- two panels** - **Recent run:** last run timestamp,
selected scenario, status, packet count, and link to view results. -
**How it works:** a simple 4-step visual:
`Generate packets → Inspect → Decide → Measure`.

**Bottom section** - `Recommended demo` card describing the prepared
"Web session with unsolicited traffic" scenario. - A compact list of
recent simulation runs, if run history exists.

### Empty state

When no run has happened, show helpful copy and a single
`Run the sample simulation` CTA. Do not display fake historical metrics.

------------------------------------------------------------------------

## 4.2 Live Simulation page

**Purpose:** The main presentation/demo page. The user must be able to
watch packets move through the engine and understand each decision.

### Layout

**A. Page controls** - Title: `Live Simulation` - Short instruction:
`Each packet advances through the engine at a deliberate pace.` -
Scenario dropdown, defaulting to
`Web session with unsolicited traffic`. - Packet count and estimated
duration, calculated from the selected scenario. - Controls: `Start`,
`Pause`, `Resume`, `Stop`, `Restart`. - Speed selector:
`2 seconds / packet` as the default and recommended demo setting.
Optional slower setting: `3 seconds / packet`. Do not default to rapid
animation on this page.

**B. Main traffic-flow canvas**

Build a large horizontal flow with three visually distinct stages:

1.  **Traffic source / packet queue**
    -   A vertical queue of the next packets.
    -   Each packet tile shows packet ID, source IP:port, destination
        IP:port, protocol, and a short purpose label.
    -   Pending packets use neutral colors.
2.  **Firewall engine**
    -   A central, large card labelled with the active firewall model.
    -   Inside it, display the processing steps as a small vertical
        checklist:
        -   Validate packet
        -   Check connection state (stateful model only)
        -   Evaluate ordered rules
        -   Apply final decision
    -   Highlight the current step in peach/taupe. Completed steps use
        neutral check icons.
    -   Show the current rule being evaluated, if any, and why it
        matches or does not match.
3.  **Decision lanes**
    -   An `ALLOWED` lane and a `BLOCKED` lane on the right.
    -   Allowed packets enter the green lane; blocked packets enter the
        red lane.
    -   Each completed packet tile must retain its packet ID and final
        outcome.
    -   Keep the red/green colors confined to these outcome areas and
        their related labels/icons.

**Packet animation** - Animate only the current packet moving from queue
→ engine → its decision lane. - The engine processes **one packet at a
time** on this page. - A packet's journey should take approximately 2
seconds by default. Keep enough time for a presenter to read the
reason. - Use CSS transforms/opacity or the frontend animation library
already chosen; avoid excessive physics or complex 3D. - The animation
must be tied to actual backend evaluation results. Never animate a
packet as allowed or blocked before the backend returns that decision. -
While a request is pending, show `Evaluating packet…`; then animate the
packet to the returned decision lane and reveal its explanation. - If
the backend takes longer than the animation duration, wait for the real
result; do not fabricate timing or outcomes.

**C. Decision explanation panel**

Place this beside the flow canvas on wide screens or directly below it
on smaller screens.

Show for the current packet: - Packet ID. - Source and destination
address/port. - Protocol. - Decision: `ALLOWED` or `BLOCKED`. - Reason
in plain English. - Matched rule ID/name and its action, or
`No matching rule — default policy blocked` where applicable. -
Connection state, if stateful inspection is enabled: `NEW`,
`ESTABLISHED`, `REPLY`, `NOT TRACKED`, or the actual supported
equivalent. - A compact "Why?" explanation, for example:
`This TCP reply matches an established connection that was created by an earlier allowed outbound packet.`
Only display this if the backend's result supports that explanation.

**D. Live counters** - Packets processed / total. - Allowed count. -
Blocked count. - Current processing packet ID. - Progress bar,
e.g. `6 of 12 packets`.

**E. Packet event log** - A compact table beneath the flow: -
Time/sequence - Packet ID - Source → destination - Protocol - Decision -
Reason / rule - Clicking a row selects it and opens its full decision
details. - Add filters for All / Allowed / Blocked. Use green/red only
for outcome labels and icons.

### Live simulation behaviour

-   `Start` begins from packet 1.
-   `Pause` finishes no extra packet; it pauses before the next packet.
    If an evaluation is in progress, finish and record that packet, then
    pause.
-   `Resume` continues from the next unprocessed packet.
-   `Stop` stops after any in-flight evaluation is safely resolved;
    clearly mark the run as stopped/partial.
-   `Restart` resets the run progress and counters, retaining the
    selected scenario and rules.
-   Prevent duplicate clicks from starting duplicate runs.
-   Provide a reduced-motion preference. With reduced motion enabled,
    use an immediate state change and a visible step indicator while
    preserving the two-second reading interval.
-   On completion, show a concise summary and a `View metrics` CTA.

------------------------------------------------------------------------

## 4.3 Compare Firewalls page

**Purpose:** Run the same packet stream through both models and show
where their decisions differ.

This page should be optimized for a quick side-by-side demonstration, so
it may run faster than Live Simulation. Default to **0.3--0.5 seconds
per packet per visual batch**, or use a short batch animation; provide
`Normal` and `Fast demo` speed settings. Explain that the faster
animation changes only presentation speed, not the packet order or
evaluation logic.

### Layout

**A. Configuration bar** - Scenario selector. - Packet count. - Rule set
selector, ideally `Current rules`. - `Run comparison` button (distinct
from the Live Simulation button and clearly labelled). -
`Reset comparison`. - Speed selector: `Normal` / `Fast demo`.

**B. Two parallel firewall columns** - Left column:
`Packet-Filtering Firewall` with a stateless label. - Right column:
`Stateful-Inspection Firewall` with a state-tracking label. - Both show
their own queue, current packet, processing state, allowed count,
blocked count, and progress. - A shared packet sequence indicator makes
it obvious that packet N is being compared with packet N on the other
side. - The two models should evaluate the same packet data and same
ordered policy rules, but maintain separate state and separate
counters. - Run both models independently; do not reuse one model's
result as the other's result.

**C. Difference strip** After or during each paired decision, show: -
`Same decision` when both outcomes match. - `Different decision` when
outcomes differ. - Clicking a difference opens the packet's side-by-side
explanation. - For each difference, explain the actual cause: for
example, stateful connection recognition, invalid packet handling, or a
policy-rule difference. Do not assert that stateful inspection is always
more permissive or always more secure.

**D. Comparison table** Columns: - Packet ID - Source → destination -
Protocol - Packet-filtering decision - Stateful decision -
Same/different - Explanation

Highlight differing decisions with a neutral peach background and a
small `DIFFERENCE` label. Use green/red only within the outcome cells.

**E. Results CTA** - `View comparison metrics` - `Inspect differences` -
`Run again`

### Fair-comparison requirements

-   Use one immutable packet list for both firewalls.
-   Use the same rule list and rule order for both models.
-   Use identical packet validation rules unless the comparison
    explicitly documents a model difference.
-   Reset state and statistics before every fresh run.
-   Ensure deterministic packet order and stable IDs.
-   Show the number of packets evaluated by each firewall. If one side
    errors, mark the run incomplete rather than reporting a misleading
    comparison.
-   Explain the model's default policy, especially whether unmatched
    packets are blocked.
-   Do not manufacture differences merely to make the comparison look
    impressive. The scenario should expose genuine differences in
    connection-tracking behaviour.

------------------------------------------------------------------------

## 4.4 Rules page / Rule Editor

**Purpose:** Let a presenter edit firewall policy quickly without
understanding JSON.

### Layout

**Header** - Title: `Firewall Rules` - Subtitle:
`Rules are evaluated from top to bottom. The first matching rule decides the result.` -
Actions: `Add rule`, `Restore demo rules`, `Export rules` (optional for
MVP).

**Rule table** Columns: 1. Priority / drag handle. 2. Rule name and
short description. 3. Source IP. 4. Destination IP. 5. Protocol. 6.
Destination port. 7. Action. 8. Enabled state, if enabled/disabled is
implemented. 9. Row actions: Edit, Duplicate, Delete.

Use a clear priority number and make order meaningful. Support move
up/down buttons as a keyboard-accessible alternative to drag-and-drop.
Display a small `FIRST MATCH WINS` note above the table.

**Add/Edit rule drawer or modal** Fields: - Rule name (new UI field;
backend model needs to support it or safely generate a name). - Source
IP/CIDR or `Any`. - Destination IP/CIDR or `Any`. - Protocol: `Any`,
`TCP`, `UDP`, `ICMP`. - Destination port: specific port or `Any`. -
Action: `Allow` or `Block`. - Optional description. - Save / Cancel.

**Validation and help** - Validate IP addresses/CIDRs, ports (1--65535),
protocol, and action in both frontend and backend. - If ICMP is
selected, disable the port field or explain how the engine treats it; do
not silently imply ICMP has TCP/UDP ports. - If a rule combination is
not supported by the current engine, explain it rather than accepting a
rule that will never behave as the UI suggests. - Show inline errors
beside fields. - Require confirmation before deleting a rule. - Warn
when moving a broad rule above a narrow rule because first-match-wins
ordering can change behaviour. - Provide an `Unsaved changes` indicator
and a clear save action. - On successful save, show a small neutral
confirmation and record a new ruleset version.

**Demo presets** Include named, resettable rule presets: -
`Balanced web access` - `Strict inbound` -
`Teaching: show rule-order effects`

Each preset should have a concise explanation and should be saved as a
known configuration. Keep the current rules available as the default
preset until the user explicitly chooses another.

------------------------------------------------------------------------

## 4.5 Metrics page

**Purpose:** Make the results attractive and self-explanatory to someone
who has not studied firewall terminology.

This page can use vivid, carefully chosen chart colors, but outcome
status must remain consistent: allowed = green, blocked = red. The main
application remains neutral.

### Layout

**A. Summary row** - Total packets evaluated. - Allowed packets. -
Blocked packets. - Decision disagreement count for comparison runs. -
Run duration (label clearly as simulated duration or wall-clock
runtime).

Every metric card needs: - A short title. - A large value. - One
sentence explaining what it means. - A tooltip or help link for the
exact formula.

**B. Outcome distribution** - Stacked bar or donut chart for allowed vs
blocked packets. - Show counts and percentages together. - Always
include a text summary beneath the chart for accessibility. - For a
comparison run, show both firewall models side by side.

**C. Comparison chart** Use grouped bars for each firewall: - Allowed
count. - Blocked count. - Total evaluated.

Do not mix different units in one unlabeled axis. Prefer separate
compact charts if a shared scale would mislead.

**D. Decision agreement** - `Same decisions`: number and percentage. -
`Different decisions`: number and percentage. - A concise explanation of
what disagreement means. - A list of differing packet IDs that links to
packet details.

**E. Performance and state** Where measured, show: - Average evaluation
latency (ms/packet). - Total evaluation runtime. - Peak active tracked
connections. - Connection-table hits / established replies recognized,
if instrumented. - Invalid packets blocked. - Default-policy blocks.

Do not show metrics that the backend does not actually collect. If a
metric is not implemented, mark it `Not measured` or omit it; never
invent data.

**F. Metric glossary**

Include simple, always-visible definitions: - **Allowed rate:** allowed
packets divided by evaluated packets. - **Blocked rate:** blocked
packets divided by evaluated packets. - **Decision disagreement:**
packets for which the two firewall models return different outcomes,
divided by packets evaluated by both models. - **Average evaluation
latency:** total measured evaluation time divided by number of packets
evaluated. State whether this is server-side engine time or end-to-end
request time. - **Connection tracking:** the stateful firewall's memory
of eligible earlier connections. - **Default-policy blocks:** packets
blocked because no rule matched and the default action is block.

For every percentage, display numerator and denominator on hover or in
the detail panel. Avoid ambiguous percentages.

**G. Empty/error states** - Before a run, explain:
`Run a simulation to generate metrics.` - If the run was partial, mark
metrics `Partial run`. - If one firewall failed, do not compare
incomplete results as though both finished.

------------------------------------------------------------------------

## 4.6 Packet Log page

**Purpose:** A searchable, inspectable record of decisions across the
latest run.

### Layout

-   Search by packet ID, source IP, destination IP, port, or protocol.
-   Filters: Allowed / Blocked / All, model, scenario, and reason
    category where supported.
-   Columns: sequence, packet ID, source, destination, protocol,
    outcome, matched rule, reason.
-   Click a row to open a detail drawer with the full packet, rule,
    connection state, and evaluation explanation.
-   Use pagination or virtualized rows if packet counts become large.
-   Provide `Download CSV` only if a backend/export route is
    implemented; otherwise leave it out of the UI.

Do not treat this log as real-world traffic. Label it as synthetic
simulation data.

------------------------------------------------------------------------

## 5. Synthetic traffic scenarios

Scenarios must be designed to demonstrate realistic traffic patterns and
genuine behavioural differences. Use documentation-only IP ranges in
demo data where possible (for example, `192.0.2.0/24`,
`198.51.100.0/24`, and `203.0.113.0/24`) and private IP ranges where
useful. Clearly label all addresses as simulated.

Every packet should have: - Stable ID, e.g. `PKT-001`. - Sequence
number. - Scenario name. - Source IP and source port when applicable. -
Destination IP and destination port when applicable. - Protocol. - A
human-readable purpose label. - Expected real-world meaning. - Optional
`reply_to` or `flow_id` metadata for scenario generation, not a bypass
of firewall evaluation. - A short explanation of why the packet is in
the scenario.

Do not preassign the actual result as the evaluation input. Expected
outcomes may be used by tests, but the firewall engine must calculate
the result from the packet and rules.

### 5.1 Default scenario: `Web session with unsolicited traffic`

Target approximately 12--16 packets so the default demo is short enough
to present while showing meaningful behaviour. At 2 seconds per packet,
12 packets take about 24 seconds plus transitions and explanation time.

Use a consistent default policy with explicit outbound web access and
default block. Ensure rules are the same for both firewall models.

Suggested sequence:

  -----------------------------------------------------------------------------
  ID                Simulated packet  Real-life              Demonstration
                                      interpretation         purpose
  ----------------- ----------------- ---------------------- ------------------
  PKT-001           Internal client   Client starts an HTTPS Establish a
                    TCP SYN to web    connection             permitted outbound
                    server port 443                          connection

  PKT-002           Web server TCP    Server replies to the  Demonstrate
                    reply to the      earlier connection     stateful reply
                    client ephemeral                         recognition versus
                    port                                     stateless rules

  PKT-003           Internal client   Client starts an HTTP  Show another
                    TCP SYN to web    connection             explicit web rule
                    server port 80                           

  PKT-004           Web server TCP    Reply to the HTTP      Repeat the
                    reply to the      connection             stateful behaviour
                    client ephemeral                         with a second flow
                    port                                     

  PKT-005           External host TCP Unsolicited inbound    Demonstrate
                    SYN to internal   SSH attempt            default inbound
                    service port 22                          blocking

  PKT-006           Internal client   Attempt to use Telnet  Demonstrate
                    TCP SYN to                               explicit deny-rule
                    external port 23                         priority

  PKT-007           Internal client   DNS lookup             Show UDP policy
                    UDP packet to DNS                        and that only
                    port 53                                  supported state is
                                                             tracked

  PKT-008           DNS server UDP    DNS response           Demonstrate reply
                    reply to client                          handling only if
                    ephemeral port                           the engine's state
                                                             model supports it

  PKT-009           Internal client   Another HTTPS flow     Show repeated
                    TCP packet to                            allowed traffic
                    external port 443                        without reusing
                                                             another flow's
                                                             state

  PKT-010           External host TCP Unsolicited inbound    Show stateful
                    packet with no    data                   rejection if the
                    matching prior                           packet is not an
                    connection                               established reply
                                                             and policy does
                                                             not allow it

  PKT-011           Packet with       Malformed/suspicious   Show input
                    invalid source IP packet                 validation and
                                                             invalid-packet
                                                             blocking

  PKT-012           Internal client   Unapproved service     Show
                    UDP packet to an  traffic                default-policy
                    unapproved                               blocking
                    destination port                         

  PKT-013           TCP packet to a   Rule-order             Show
                    port covered by a demonstration          first-match-wins
                    broad allow rule                         when a block rule
                                                             is placed
                                                             above/below a
                                                             broad allow

  PKT-014           Reply packet for  No valid allowed       Confirm a blocked
                    a previously      connection exists      attempt does not
                    blocked                                  create connection
                    connection                               state
                    attempt                                  
  -----------------------------------------------------------------------------

**Important implementation detail:** A real TCP handshake is more than a
source/destination tuple. The current simulator may only model
connection tuples and replies, not TCP flags or full handshake
validation. Do not label a tuple match as full TCP protocol validation.
If SYN/ACK/FIN/RST flags are not implemented, call these "simulated
connection-start/reply events" in the UI.

### 5.2 Additional scenario presets

**`Strict inbound`** - Several outbound web sessions with valid
replies. - Unsolicited inbound SSH and RDP-like attempts. - An inbound
packet that resembles a reply but does not match tracked state. - A
blocked outbound service attempt. - Use this to explain the benefit and
limits of connection tracking.

**`Rule order matters`** - A broad allow rule and a narrow block rule. -
Run once with the narrow block first, then with it after the broad
allow. - Show how first-match-wins changes the result in both models. -
Use identical packets and explicitly show the ruleset order in the
results.

**`Mixed enterprise traffic`** - HTTPS, DNS, NTP-like UDP traffic, a
denied legacy service, an allowed reply, and unsolicited inbound
traffic. - Do not imply protocol-specific security inspection that the
engine does not implement.

### 5.3 Ensure visible but honest differences

-   Stateful reply recognition is the most direct source of comparison
    differences. To demonstrate it, include an outbound flow allowed by
    a rule and its inbound reply.
-   A stateless packet filter may block the reply if the same policy
    does not explicitly allow that inbound tuple; a stateful firewall
    can accept it because it belongs to a tracked flow.
-   Also include unsolicited inbound packets to show that stateful
    inspection does not blindly allow all inbound packets.
-   Include blocked connection attempts and ensure they do not create
    state.
-   Include UDP examples only with clearly documented
    connection-tracking semantics.
-   If the current packet model cannot distinguish a genuine reply from
    an unrelated packet sharing a tuple, document that limitation or add
    minimal flow metadata/flags before claiming high-fidelity stateful
    inspection.
-   Keep expected results in automated tests so changes to rules do not
    silently erase the intended teaching differences.
-   Do not tune scenarios to claim one firewall is universally better.
    Present the trade-off and the precise reason for each outcome.

------------------------------------------------------------------------

## 6. Backend audit and required changes

The existing Python implementation should be reused as the engine
foundation rather than replaced wholesale. The current desktop UI uses
Tkinter and cannot run directly as a browser interface. Introduce an
HTTP API layer and keep the core engine independent of the frontend.

### 6.1 Current modules to retain and review

-   `firewall/packet.py`: packet data model and validation.
-   `firewall/rules.py`: rule model, loading/saving, ordering.
-   `firewall/engine.py`: rule evaluation and statistics.
-   `firewall/state.py`: stateful connection tracking.
-   Existing tests for rule evaluation, stateful replies, timeout
    behaviour, malformed packets, and stats.
-   Existing JSON rules as the baseline demo configuration.

Do not delete working tests simply because the UI changes.

### 6.2 `packet.py` changes

Review and, where necessary, extend the packet model to support the UI
and scenario generator.

Required: - Stable `packet_id` and `sequence` metadata should live in
the scenario/run layer or be added in a backwards-compatible way. - Keep
source/destination IP, ports, and protocol validation centralized. -
Represent ports as absent/null for ICMP instead of inventing TCP/UDP
ports. - Provide a JSON-safe serializer for API responses. - Add
optional TCP flags only if they will actually be used by the engine;
otherwise avoid exposing unsupported flags in the UI. - Keep backward
compatibility with existing tests and callers.

### 6.3 `rules.py` changes

Required: - Preserve first-match-wins order. - Add a stable `rule_id`
and human-readable `name` to each rule. Existing rules must load through
a migration/defaulting path that assigns stable IDs/names when absent. -
Add an `enabled` flag only if the engine will reliably skip disabled
rules and the UI needs it. - Support IP/CIDR matching only if
implemented consistently in backend validation and evaluation. If not
implemented, the UI must accept only exact IP addresses and `Any`. -
Validate protocols, actions, ports, and address fields in the backend,
not only in the frontend. - Return useful validation errors for the rule
editor. - Make save operations atomic where possible: write a temporary
file, then replace the rules file. - Do not silently reset valid user
rules after a parse error; report the error and provide a deliberate
`Restore demo rules` action. - Keep the existing JSON format readable
and easy to inspect.

### 6.4 `engine.py` changes

Required: - Preserve the current rule-evaluation semantics unless tests
explicitly justify a change. - Return structured, consistent evaluation
results with: - packet ID/sequence where available, - `action`, -
`matched_rule_id`, - `matched_rule_name`, - `reason_code`, - `reason`
(plain-English text), - `connection_state`, - `processing_time_ms` if
reliably measured. - Standardize reason codes such as: -
`INVALID_PACKET` - `ESTABLISHED_CONNECTION` - `RULE_ALLOW` -
`RULE_BLOCK` - `DEFAULT_BLOCK` - `NO_TRACKABLE_STATE` - Make clear
whether the action came from state tracking, a matching rule, or the
default policy. - Track counters separately for each engine instance and
each run. - Ensure invalid packets are safely rejected without crashing
the run. - Ensure a blocked packet does not create a tracked
connection. - Ensure only supported TCP/UDP flows are tracked and
document how replies are identified. - Ensure statistics cannot leak
from one comparison run into the next. - Make stateful and stateless
firewall behaviour explicit. Prefer separate evaluator
configurations/classes that share validation and rule matching code,
rather than using a single ambiguous boolean that makes the two models
hard to compare. - Keep `FirewallEngine` API compatibility where
practical, or update all callers/tests in the same change.

### 6.5 `state.py` changes

Required: - Keep the idle timeout configurable and testable. - Track
only supported protocols and packets with the necessary ports. - Expose
safe, read-only connection summary data for the UI (not mutable internal
objects). - Track enough metadata to explain why a packet matched an
established connection. - Ensure a state-table hit is only reported when
the packet really matches the engine's documented tuple/direction
logic. - Document limitations: tuple-based tracking is not equivalent to
a full TCP state machine unless TCP flags and handshake states are
implemented. - Ensure reset clears state and counters for a new run.

### 6.6 Add a scenario/data module

Create a dedicated module, e.g. `backend/app/scenarios.py` or
`firewall/scenarios.py`, that: - Defines scenario presets as data. -
Generates deterministic packet lists with stable IDs. - Includes
explanatory packet labels and expected outcomes for tests only. - Does
not pre-fill evaluated decisions. - Provides a scenario listing API. -
Validates scenario IDs. - Returns the same packet stream for both models
in a comparison run. - Supports a fixed random seed if optional random
traffic is later added.

### 6.7 Add a run/simulation service

Create a dedicated service layer,
e.g. `backend/app/services/simulation_service.py`, to: - Start a run
with a chosen scenario and firewall model. - Create a fresh
engine/state/statistics instance per run. - Process one packet on demand
for the slow Live Simulation page. - Support pause/resume/stop at the
API/session layer without corrupting engine state. - Run a paired
comparison against the same packet list using independent engine
instances. - Persist run metadata and per-packet results in memory for
the MVP, or in a small local database if history is required. - Mark
runs as `running`, `paused`, `completed`, `stopped`, or `failed`. - Keep
a run ID, scenario ID, model configuration, ruleset snapshot/version,
timestamps, processed count, and results. - Return partial-run state
honestly if stopped before all packets are evaluated. - Avoid global
mutable engine instances shared between unrelated sessions.

### 6.8 Add a FastAPI backend

Recommended API layer: FastAPI, with Pydantic request/response models.

Suggested routes:

  --------------------------------------------------------------------------------------------
  Method                  Endpoint                                     Purpose
  ----------------------- -------------------------------------------- -----------------------
  `GET`                   `/api/health`                                Health check for
                                                                       hosting

  `GET`                   `/api/scenarios`                             List available
                                                                       synthetic scenarios

  `GET`                   `/api/rules`                                 Read current rules and
                                                                       order

  `PUT`                   `/api/rules`                                 Validate and replace
                                                                       the ordered ruleset

  `POST`                  `/api/rules/reset`                           Restore the demo rules
                                                                       after confirmation in
                                                                       the UI

  `POST`                  `/api/simulations`                           Create a single-model
                                                                       run

  `POST`                  `/api/simulations/{run_id}/step`             Evaluate the next
                                                                       packet and return its
                                                                       decision

  `POST`                  `/api/simulations/{run_id}/pause`            Pause the run

  `POST`                  `/api/simulations/{run_id}/resume`           Resume the run

  `POST`                  `/api/simulations/{run_id}/stop`             Stop the run cleanly

  `GET`                   `/api/simulations/{run_id}`                  Get run status and
                                                                       summary

  `GET`                   `/api/simulations/{run_id}/packets`          Get paginated packet
                                                                       results

  `POST`                  `/api/comparisons`                           Run both models on one
                                                                       identical packet stream

  `GET`                   `/api/comparisons/{comparison_id}`           Retrieve comparison
                                                                       summary/results

  `GET`                   `/api/comparisons/{comparison_id}/metrics`   Retrieve computed
                                                                       comparison metrics

  `GET`                   `/api/metrics/{run_id}`                      Retrieve single-run
                                                                       metrics
  --------------------------------------------------------------------------------------------

Implementation notes: - Use Pydantic models for requests and
responses. - Return appropriate HTTP status codes and structured
errors. - Validate all user-controlled fields server-side. - Restrict
CORS to the deployed frontend origin(s) and localhost development
origin(s), not `*` in production. - Do not expose filesystem paths or
stack traces to clients. - Do not execute shell commands or create real
firewall rules from API requests. - Avoid making the slow simulation
depend on a long-running HTTP request. Prefer one packet per step
request; the frontend waits for the configured interval between steps. -
For comparisons, process both engines on the same server-side packet
list and return per-packet paired outcomes. The UI can animate those
results quickly. - If the MVP stores runs only in memory, document that
runs reset when the server restarts and may not be shared across
multiple instances. - If JSON files are used for rules on a free host,
document that the filesystem may be ephemeral. Do not promise permanent
persistence without a persistent database/volume.

### 6.9 Metrics service

Create one shared, tested metrics function that derives metrics from
recorded results. At minimum: - total packets evaluated, - allowed count
and rate, - blocked count and rate, - invalid packet count, -
default-policy block count, - matched allow-rule count, - matched
block-rule count, - number of completed packets, - completion status.

For comparison: - packets evaluated by both models, - same-decision
count, - different-decision count, - disagreement rate, - packet IDs
where outcomes differ, - per-model allowed/blocked counts and rates.

Optional if properly measured: - engine processing time per packet and
average/p50/p95 latency, - maximum active state entries, -
connection-state hits, - state-table misses.

Metrics formulas must be computed from actual results, not hard-coded
for the demo. Define zero-denominator behaviour, e.g. show `—` rather
than dividing by zero.

### 6.10 Suggested backend layout

Adapt to the current repository instead of blindly duplicating files:

``` text
netfort/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── rules.py
│   │   │   ├── scenarios.py
│   │   │   ├── simulations.py
│   │   │   ├── comparisons.py
│   │   │   └── metrics.py
│   │   ├── schemas/
│   │   │   ├── packet.py
│   │   │   ├── rule.py
│   │   │   ├── simulation.py
│   │   │   └── metrics.py
│   │   ├── services/
│   │   │   ├── simulation_service.py
│   │   │   ├── comparison_service.py
│   │   │   └── metrics_service.py
│   │   └── scenarios.py
│   ├── firewall/
│   │   ├── packet.py
│   │   ├── rules.py
│   │   ├── engine.py
│   │   └── state.py
│   ├── data/
│   │   └── rules.json
│   ├── tests/
│   ├── requirements.txt
│   └── render.yaml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── plan.md
└── README.md
```

This is a target structure, not a command to duplicate existing modules.
Reuse and move existing files deliberately, then update imports and
tests.

------------------------------------------------------------------------

## 7. Frontend implementation plan

### 7.1 Recommended stack

-   React + Vite.
-   TypeScript preferred for reliable API contracts; JavaScript is
    acceptable if the existing project is already JS-only.
-   React Router for page navigation.
-   Tailwind CSS or CSS modules; choose one primary styling approach and
    avoid mixing several competing systems.
-   Lucide React for icons.
-   Recharts for metrics charts.
-   Framer Motion or lightweight CSS transitions for packet animation.
    Use one animation approach.
-   Fetch or Axios for API calls; use one consistently.

### 7.2 Component structure

Suggested reusable components: - `AppShell` - `Sidebar` - `TopBar` -
`PageHeader` - `Button` - `MetricCard` - `OutcomeBadge` - `PacketCard` -
`PacketFlow` - `FirewallEnginePanel` - `DecisionDetails` -
`SimulationControls` - `ProgressIndicator` - `PacketLogTable` -
`RuleTable` - `RuleEditorForm` - `ComparisonPanel` -
`ComparisonDifferenceRow` - `MetricChartCard` - `EmptyState` -
`ErrorState` - `ConfirmDialog` - `Tooltip`

Shared components should enforce the same neutral surfaces, spacing,
typography, borders, and outcome semantics.

### 7.3 State management

Keep the MVP straightforward. Use React state and custom hooks unless
the application genuinely needs a larger state library.

Suggested hooks: - `useScenarios()` - `useRules()` -
`useSimulation(runId)` - `useComparison(comparisonId)` -
`useMetrics(runId)`

Requirements: - Keep server-owned evaluation results in API responses. -
Keep transient UI state (selected packet, open modal, animation
progress) in the frontend. - Do not create a second frontend-only
firewall engine. - Do not calculate a decision in the UI. - Ensure stale
API responses from a previous run cannot overwrite the current run. -
Abort or ignore obsolete requests when the user restarts a simulation. -
Display loading, empty, validation, and server-error states explicitly.

### 7.4 Responsive behaviour

-   Desktop: full left sidebar and wide flow canvas.
-   Tablet: compact sidebar or drawer; flow may wrap into source →
    engine → outcome rows.
-   Mobile: sidebar drawer; one-column packet flow; controls wrap
    cleanly; packet detail appears below the engine.
-   Comparison page: stack the two firewalls vertically on mobile, with
    the same packet index shown for both.
-   Tables: horizontal scrolling or compact row cards, never clipped
    columns without a way to inspect them.

------------------------------------------------------------------------

## 8. Animation and timing requirements

### Live Simulation

-   Default packet interval: **2,000 ms per packet**.
-   The backend decides each packet; the frontend schedules the next
    step.
-   Sequence: request/evaluate → receive result → reveal explanation →
    animate to outcome lane → wait for interval → next packet.
-   If evaluation itself takes longer than the interval, never start the
    next packet until the result is received.
-   Pause/stop must not duplicate a packet or skip a result.
-   Show the packet ID during its entire journey.
-   The progress counter increments only after a packet result has been
    received and recorded.
-   On network failure, keep the current packet unresolved, show a retry
    action, and do not count it as allowed or blocked.

### Compare Firewalls

-   Use a separate compare control and a faster default.
-   The backend can return all paired results in one response for the
    small, fixed demo dataset; animate each pair in sequence.
-   Never call the slow Live Simulation stepping loop just to implement
    comparison animation if a paired-comparison endpoint is available.
-   Fast mode may shorten transitions but must not change evaluation
    results, packet ordering, rules, or metrics.
-   Provide a "Skip animation" option if useful for repeat demos, but
    retain the full results table.

------------------------------------------------------------------------

## 9. Testing and acceptance criteria

### 9.1 Existing engine regression tests

Run all existing tests after every backend change. Preserve coverage
for: - packet validation, - rule matching, - first-match-wins
ordering, - invalid IP/port/protocol handling, - stateful reply
matching, - blocked request not creating state, - idle timeout and timer
refresh, - unsupported/untrackable packets, - stateful mode disabled, -
state reset, - correct statistics.

### 9.2 New backend tests

Add tests for: - each scenario returning stable packet IDs and
deterministic order, - both models receiving exactly the same packet
list, - fresh connection state for every new run, - the same ruleset
snapshot being used by both models, - a valid reply to an allowed flow
creating a real, documented difference when policy is configured to
expose it, - unsolicited inbound traffic not being accepted merely
because stateful mode is enabled, - blocked attempts not creating
state, - rule reordering changing decisions only where first-match-wins
semantics predict it, - invalid rules rejected with useful messages, -
metrics computed correctly from known result fixtures, - empty runs and
partial runs, - API errors and unknown run/scenario IDs, - independent
users/runs not sharing mutable engine state.

### 9.3 Frontend acceptance checklist

-   Sidebar icons and active page state work on every route.
-   Live simulation processes one packet at a time with a 2-second
    default interval.
-   Each displayed outcome comes from the backend.
-   The explanation names the matched rule or the default-block reason.
-   Pause, resume, stop, and restart do not duplicate or lose packets.
-   Compare page uses a separate faster control and compares the same
    sequence.
-   Difference rows explain why the decisions differ.
-   Rule editor supports add/edit/delete/reorder, with inline
    validation.
-   Rule changes affect a subsequent run.
-   Metrics values and charts agree with the packet results and
    formulas.
-   Allowed packets are always green and blocked packets are always red;
    neither color is used for unrelated UI elements.
-   Loading, empty, error, partial-run, and completed states are
    implemented.
-   Layout remains usable at desktop, tablet, and mobile widths.
-   Keyboard focus, accessible labels, and non-color outcome text are
    present.

### 9.4 Demo acceptance scenario

A successful live demo should take approximately 1--2 minutes: 1. Open
Dashboard and choose the default scenario. 2. Start Live Simulation and
explain 3--5 packets while the engine runs at 2 seconds per packet. 3.
Point out a rule match, a default block, and a stateful reply. 4. Open
Rules, change or reorder one rule, and rerun. 5. Open Compare Firewalls
and run the same scenario in fast mode. 6. Open Metrics and explain
allowed rate, blocked rate, disagreement rate, and the packets
responsible for the difference. 7. Reset the demo to its baseline
configuration.

------------------------------------------------------------------------

## 10. Deployment and configuration

### Backend

-   Deploy FastAPI as a Python web service.
-   Add a health endpoint.
-   Use environment variables for frontend origin and configuration.
-   Keep secrets out of source control.
-   Pin or bound dependencies in `requirements.txt`.
-   Configure CORS to the actual deployed frontend origin.
-   Be explicit that in-memory runs disappear on restart and that local
    file changes may not persist on an ephemeral host.
-   Use persistent storage only if the demo truly needs rules/run
    history to survive restarts.

### Frontend

-   Build and deploy the Vite frontend as a static site.
-   Configure a single environment variable such as `VITE_API_BASE_URL`
    for the backend base URL.
-   Avoid hard-coded localhost API URLs in production builds.
-   Add a friendly API-unavailable state that explains the backend may
    be sleeping or unavailable, with a retry action.

### Repository hygiene

-   Add `.env.example` with safe placeholders.
-   Add `.gitignore` entries for `.venv/`, `node_modules/`, build
    output, `.env`, logs, caches, and temporary model/data files.
-   Document local startup commands for backend and frontend.
-   Document deployment steps and the synthetic-only safety boundary.
-   Keep test rules and production/demo rules clearly named; never
    overwrite a user's customized rules silently.

------------------------------------------------------------------------

## 11. Implementation order

Implement in the following order to reduce risk and keep each stage
demonstrable.

### Phase 1 --- Audit and lock down engine behaviour

1.  Run the current test suite and record baseline results.
2.  Review the current engine, rules, packet, and state models.
3.  Add stable rule IDs/names and structured reason codes without
    breaking old rules.
4.  Separate stateless packet-filtering behaviour from stateful
    inspection explicitly.
5.  Create deterministic scenarios and test fixtures.
6.  Add metrics functions and verify formulas with hand-calculated test
    cases.

**Exit condition:** Existing tests pass, new model-comparison tests
pass, and the backend can explain every decision.

### Phase 2 --- Build the API

1.  Create FastAPI app and health route.
2.  Add scenario and rule endpoints.
3.  Add single-run create/status/step/pause/resume/stop endpoints.
4.  Add comparison endpoint with paired per-packet outcomes.
5.  Add metrics and packet-result endpoints.
6.  Add request validation, structured errors, CORS, and API tests.

**Exit condition:** All simulation behaviour can be demonstrated through
API calls without Tkinter.

### Phase 3 --- Build the shared UI shell

1.  Set up React/Vite and routing.
2.  Implement the palette and design tokens.
3.  Build sidebar, header, buttons, cards, badges, tables, and
    responsive layout.
4.  Connect health/scenario/rule APIs and implement loading/error/empty
    states.

**Exit condition:** All pages have a consistent shell and can navigate
without broken routes.

### Phase 4 --- Build Live Simulation

1.  Implement scenario selection and run creation.
2.  Build packet queue, engine panel, decision lanes, and detail panel.
3.  Add the 2-second step controller.
4.  Add pause/resume/stop/restart and packet log.
5.  Verify all outcomes and reasons come from backend responses.

**Exit condition:** A presenter can explain the packet journey one
packet at a time.

### Phase 5 --- Build Compare Firewalls

1.  Add the distinct `Run comparison` action and faster animation
    controller.
2.  Display both models side by side with paired packet indices.
3.  Add decision-difference rows and explanation details.
4.  Add comparison result persistence for the active session.

**Exit condition:** Both models evaluate the same stream and all visible
differences are traceable to actual engine results.

### Phase 6 --- Rules and Metrics

1.  Build rule editor and validation.
2.  Add presets, reorder actions, reset confirmation, and ruleset
    versions.
3.  Build outcome charts, disagreement charts, metric glossary, and
    packet links.
4.  Cross-check all metric values against API responses and raw packet
    outcomes.

**Exit condition:** A presenter can change policy and show its impact on
the same scenario.

### Phase 7 --- Polish and deploy

1.  Add keyboard accessibility, reduced-motion behaviour, responsive
    layout, and error states.
2.  Run backend tests and frontend production build.
3.  Test a complete demo on the deployed frontend/backend.
4.  Confirm rules persistence expectations and document limitations.
5.  Verify the synthetic-only notice and ensure no real traffic or host
    firewall operations exist.

**Exit condition:** The deployed demo is reproducible, safe, visually
consistent, and understandable without developer tools.

------------------------------------------------------------------------

## 12. Non-goals for the demo MVP

Do not implement these unless the core demo is stable and there is a
clear reason: - Real packet capture or raw socket networking. -
Modifying Windows, Linux, or router firewall settings. - Deep packet
inspection or payload analysis. - A full TCP state machine unless it is
a deliberate research extension. - Authentication and multi-tenant
administration. - Complex user/role management. - Live external
threat-intelligence feeds. - A large database or event-streaming
infrastructure. - Real-world security claims based only on synthetic
scenarios. - Decorative 3D effects or complicated network maps.

These features add risk and complexity without helping the primary
educational comparison.

------------------------------------------------------------------------

## 13. Definition of done

NetFort is ready for the intended demo when:

-   The browser UI has a left vertical icon sidebar and consistent
    neutral styling based on `#FFDBBB`, `#CCBEB1`, `#997E67`, and
    `#664930`.
-   Green is reserved for accepted/allowed packets and red for
    rejected/blocked packets.
-   The Live Simulation visibly moves each synthetic packet through the
    engine at approximately 2 seconds per packet.
-   Every packet outcome and explanation is derived from backend
    evaluation.
-   The Compare page uses a separate faster simulation control and
    compares identical packet streams under identical rule ordering.
-   The synthetic scenarios produce at least one genuine, explainable
    difference between stateless and stateful models.
-   The Metrics page uses vivid, readable charts and defines its
    formulas in plain language.
-   The Rules page makes rule creation, editing, deletion, and ordering
    easy and safe.
-   Existing tests remain intact and pass; new backend and frontend
    checks cover the demo flow.
-   The application clearly identifies itself as a simulator and never
    handles real network traffic or changes the host firewall.
-   The complete demo can be run repeatedly and reset to a known
    baseline without confusing stale state or metrics.
