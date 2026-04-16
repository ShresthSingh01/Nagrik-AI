# Phase 1: Design Tokens & Base Theme - Context

Implementation decisions for establishing the NagrikAI "Vishwa" brand and design foundation.

## Decisions

### Visual Identity
- **Primary Color**: `#1A237E` (Indigo) - Used for headers, primary text, and active states.
- **Accent Color**: `#FF9800` (Saffron) - Reserved for action-driving elements (Primary Buttons).
- **Surface Color**: `#FFFFFF` (Pure white) for accessibility.
- **Radius**: `12px` (Soft but modern corners).

### Typography
- **Headings**: `Outfit` font family. High contrast Ratio.
- **Body**: `Inter` font family.
- **Scale**: Base font size set to `18px` to ensure readability for rural users.

### Component Layout
- **Navigation**:
  - **Mobile**: Bottom navigation bar (3 items: Dashboard, Scan, History).
  - **Desktop**: Persistent side-navigation.
- **Accessibility**: All buttons must have a minimum `48px` touch target.
- **Content Density**: Spacious. Maximize whitespace between sections.

### Architecture
- **Tokens**: Centralized in `index.css` via `:root` variables.
- **Framework**: Vanilla CSS variables. Avoid hardcoded hex values in components.

## Gray Areas Resolved
- **Typography**: Locked to 18px base.
- **Shell**: Locked to mobile bottom-nav for one-handed usage.
- **Voice**: User-initiated playback confirmed.
- **Auth**: No login visitor mode confirmed.

## Constraints & Assumptions
- **Assumption**: Users are primarily on mobile.
- **Constraint**: Must remain lightweight (minimal heavy images).
