# Installed Accessibility Skills Guide

## Overview

This project now has access to **27 accessibility skills** from [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills). These skills are installed in the `skills/` directory and are available to GitHub Copilot and other AI agents.

## Installed Skills

All skills are located in `/skills/` directory:

### Web Dashboard Skills (Critical for AEDES)

1. **maps/** - Geospatial Data Visualization Accessibility
   - Best practices for accessible maps and geospatial data
   - ARIA labels for map controls
   - Keyboard navigation for map features
   - Alternative text representations

2. **charts-graphs/** - Data Visualization Accessibility
   - Accessible chart patterns
   - Data table alternatives
   - Color contrast requirements
   - Screen reader compatibility

3. **color-contrast/** - Color and Contrast Accessibility
   - WCAG AA/AAA contrast ratios
   - Color blindness considerations
   - Sufficient luminance testing
   - Contrast checkers and tools

4. **keyboard/** - Keyboard Navigation
   - Keyboard-only navigation
   - Tab order management
   - Focus indicators
   - Keyboard shortcuts
   - Skip navigation links

5. **forms/** - Form Accessibility
   - Form field labeling
   - Error message association
   - Fieldset and legend usage
   - Form validation messaging
   - Accessibility for input types

6. **content-design/** - Clear and Accessible Content
   - Plain language principles
   - Heading hierarchy
   - List structures
   - Link text clarity
   - Reading level optimization

7. **plain-language/** - Plain Language Standards
   - Simple sentence structures
   - Active voice usage
   - Meaningful bullet points
   - Technical term definitions
   - Readability metrics

### Supporting Skills

8. **ACCESSIBILITY-general/** - General Accessibility Principles
9. **anchor-links/** - Anchor Link Accessibility
10. **aria-live-regions/** - Dynamic Content Accessibility
11. **audio-video/** - Multimedia Accessibility
12. **axe-rules/** - Automated Accessibility Testing Rules
13. **bug-reporting/** - Accessibility Bug Reporting
14. **ci-cd/** - Accessibility in CI/CD Pipelines
15. **image-alt-text/** - Image Alt Text Best Practices
16. **light-dark-mode/** - Light/Dark Mode Accessibility
17. **manual-testing/** - Accessibility Testing Guide
18. **mermaid/** - Diagram Accessibility
19. **navigation/** - Navigation Structure Accessibility
20. **print/** - Print Accessibility
21. **progressive-enhancement/** - Progressive Enhancement
22. **svg/** - SVG Accessibility
23. **tables/** - Table Accessibility
24. **tooltips/** - Tooltip Accessibility
25. **touch-pointer/** - Touch and Pointer Accessibility
26. **user-personalization/** - User Preference Accessibility
27. **opquast-digital-quality/** - Opquast Quality Checklist

## How to Use Skills

### With GitHub Copilot Chat
In VS Code, type in the Copilot Chat panel:

```
@workspace Use the maps skill to improve the dashboard's map accessibility
@workspace Review our color scheme using the color-contrast skill
@workspace Help me implement keyboard navigation using the keyboard skill
```

### Manual Review
Each skill is in its own directory with:
- `SKILL.md` - Main skill documentation
- `instructions.md` - Detailed implementation instructions
- `prompt.md` - AI prompt for the skill
- `examples/` - Code examples

**Example**: To review map accessibility, see `/skills/maps/SKILL.md`

## Recommended Implementation Order

### Phase 1: Foundation (Required)
1. **color-contrast** - Fix existing color issues
2. **keyboard** - Ensure keyboard navigation
3. **forms** - Fix form accessibility

### Phase 2: Enhancement (Important)
4. **maps** - Improve geospatial accessibility
5. **charts-graphs** - Enhance data visualization
6. **content-design** - Improve content clarity

### Phase 3: Polish (Nice to Have)
7. **plain-language** - Improve readability
8. **aria-live-regions** - Enhanced dynamic updates
9. **manual-testing** - Comprehensive testing

## Dashboard-Specific Implementation

### DPGA Enhancement Dashboard
**Priority**: High
**Skills to Use**:
- `maps/` - For choropleth map accessibility
- `color-contrast/` - For legend and overlay colors
- `keyboard/` - For regional selection

**Files**:
- `/dashboards/dpga_enhancement/dashboard.html`
- `/dashboards/dpga_enhancement/js/dashboard.js`
- `/dashboards/dpga_enhancement/css/main.css`

### SAT Browser Dashboard
**Priority**: High
**Skills to Use**:
- `maps/` - Satellite imagery accessibility
- `charts-graphs/` - Time series data
- `content-design/` - Layer descriptions

**Files**:
- `/dashboards/sat_browser/dashboard/index.php`
- `/dashboards/sat_browser/dashboard/rendermap.js`

### Space Apps Demo
**Priority**: Medium
**Skills to Use**:
- `forms/` - Filter and search forms
- `charts-graphs/` - Forecast charts
- `keyboard/` - Overall navigation

**Files**:
- `/dashboards/space_apps/demo/index.php`
- `/dashboards/space_apps/demo/dashboard/`

## Quick Reference: Common Tasks

### Add Accessible Map
```html
<!-- Ask Copilot -->
@workspace Use the maps skill to add accessible labels to my Mapbox map
```

### Improve Chart Accessibility
```html
<!-- Ask Copilot -->
@workspace Use the charts-graphs skill to add a data table to my visualization
```

### Check Color Contrast
```css
/* Ask Copilot */
@workspace Use the color-contrast skill to check if #FF5733 on white meets WCAG AA
```

### Make Form Accessible
```html
<!-- Ask Copilot -->
@workspace Use the forms skill to add proper labels and error messaging
```

### Improve Content Clarity
```markdown
<!-- Ask Copilot -->
@workspace Use the plain-language skill to simplify this technical documentation
```

## Testing Accessibility Against Skills

Use these tools alongside the skills:

### Browser Extensions
- [axe DevTools](https://www.deque.com/axe/devtools/) - Automated testing
- [WAVE](https://wave.webaim.org/extension/) - Visual accessibility feedback
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Chrome built-in

### Command Line Tools
```bash
# Install axe-cli for automated testing
npm install -g @axe-core/cli

# Run accessibility audit
axe https://your-dashboard-url
```

### Manual Testing Checklist
- [ ] Tab through page using keyboard only
- [ ] Check with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast with contrast checker
- [ ] Check all images have alt text
- [ ] Verify heading hierarchy
- [ ] Test with dark mode enabled
- [ ] Test on mobile/touch devices

## Resources

### External References
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Blog](https://webaim.org/blog/)
- [A11ycasts with Google Chrome](https://www.youtube.com/playlist?list=PLNYkxOF6rcICWx0C9Xc-RgEzwLvePng7V)
- [Accessibility for Developers](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

### Internal Documentation
- See [ACCESSIBILITY.md](./ACCESSIBILITY.md) for project-specific guidance
- See [CODE_REVIEW.md](./CODE_REVIEW.md) for code quality improvements

## Getting Help

### Questions About a Specific Skill?
```bash
cat /workspaces/aedesproject-uif/skills/[skill-name]/SKILL.md
```

### Need Implementation Help?
```bash
cat /workspaces/aedesproject-uif/skills/[skill-name]/instructions.md
```

### Want to See Examples?
```bash
ls -la /workspaces/aedesproject-uif/skills/[skill-name]/examples/
```

## Contributing Accessibility Improvements

When you implement an accessibility improvement:

1. Reference which skill you used: `Fixed using maps skill`
2. Describe the change: `Added ARIA labels to map controls`
3. Test thoroughly: Use browser tools and manual testing
4. Update documentation if needed

## Next Steps

1. **Review** the [ACCESSIBILITY.md](./ACCESSIBILITY.md) guide
2. **Explore** skills in `/skills/` directory
3. **Start** with Phase 1 implementation: color-contrast, keyboard, forms
4. **Test** regularly using the provided tools
5. **Document** improvements made

---

**Skills Repository**: [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills)
**Last Updated**: May 18, 2024
**Status**: All 27 skills installed and available
