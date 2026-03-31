# Frontend Design Interface Specifications

## Color Palette
| Element | Hex Code | Description |
|---|---|---|
| Background | `#F2EDE4` | Warm cream/off-white |
| Primary Dark | `#1A1A1A` | Near-black used for active states and headers |
| Accent Red | `#B34632` | Muted brick red for branding and alerts |
| Input Background | `#EBE4D8` | Slightly darker cream for input fields |
| Border / Lines | `#1A1A1A` | Sharp, thin lines (1px) for dividers |
| Text (Body) | `#6B665E` | Muted charcoal for descriptions and labels |

## Design Rules
- **Overall Style:** Minimalist, brutalist layout. Absolute zero rounded corners (`border-radius: 0`).
- **Control Toggles (AI Model & Actions):** 
  - Rectangular buttons with no rounded corners.
  - Active State: Background `#1A1A1A`, Text `#F2EDE4`.
  - Inactive State: Transparent background, thin `#1A1A1A` border.
  - Layout: Flush against each other (no gaps between buttons in a group).
