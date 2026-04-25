# macOS Tools Bundle GUI Iteration Roadmap

> Version: 1.0 | Date: 2026-04-25 | Status: Planning

## Executive Summary

This document outlines the strategic plan for evolving the 6 CLI tools (smartrename, imgcrush, clipstack, dirsnap, envguard, quickmd) into cross-platform GUI applications. The goal is to expand market reach beyond developer users to general macOS/Windows/Linux users while maintaining CLI as the core backend.

---

## 1. Market Analysis

### Current State

- **Target Users**: Developers, CLI-savvy users
- **Barrier to Entry**: Command-line knowledge required
- **Market Size**: Limited to terminal users

### GUI Opportunity

| Segment | CLI Reach | GUI Reach | Growth |
|---------|----------|-----------|--------|
| Developers | ✅ High | ✅ Medium | +20% |
| Designers | ❌ Low | ✅ High | +300% |
| Content Creators | ❌ Low | ✅ High | +500% |
| General Mac Users | ❌ None | ✅ High | +1000% |

**Projected Impact**: GUI could expand user base by 3-5x.

---

## 2. Technical Strategy

### Framework Selection

**Primary Option: PySide6 (Qt for Python)**

| Criteria | PySide6 | Tkinter | CustomTkinter | Electron |
|----------|---------|---------|---------------|----------|
| Cross-platform | ✅ Excellent | ✅ Good | ✅ Good | ✅ Excellent |
| Native look | ✅ Yes | ❌ No | ⚠️ Partial | ❌ No |
| Performance | ✅ Fast | ✅ Fast | ✅ Fast | ❌ Heavy |
| Python-native | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| Rich widgets | ✅ Excellent | ❌ Basic | ⚠️ Medium | ✅ Excellent |
| Bundle size | ⚠️ 50MB | ✅ <5MB | ✅ <5MB | ❌ 150MB+ |
| Learning curve | ⚠️ Medium | ✅ Low | ✅ Low | ⚠️ Medium |

**Recommendation**: **PySide6 (Qt)** for professional appearance and cross-platform consistency.

**Alternative for MVP**: **CustomTkinter** for faster prototyping (2-week MVP).

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│                  GUI Application                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  MainWindow │  │  ToolPanels │  │ Settings │ │
│  └─────────────┘  └─────────────┘  ┌──────────┘ │
│         │                │                │     │
│         └────────────────┼────────────────┘     │
│                          ▼                       │
│  ┌─────────────────────────────────────────────┐│
│  │           CLI Backend (Current)             ││
│  │  smartrename │ imgcrush │ clipstack │ ...   ││
│  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

**Principle**: GUI is a **wrapper** over existing CLI logic. No code duplication.

### Implementation Approach

```python
# Example: GUI calls CLI backend
from smartrename.core.renamer import rename_directory, preview_rename

class SmartRenameGUI:
    def preview_clicked(self):
        files = collect_files(self.directory)
        operations = preview_rename(files, self.mode)
        self.display_preview(operations)
    
    def execute_clicked(self):
        result = rename_directory(self.directory, self.mode)
        self.show_result(result)
```

---

## 3. Implementation Roadmap

### Phase 1: MVP (4 weeks)

**Goal**: Single unified GUI launcher with basic functionality.

**Tools Included** (Priority):
1. smartrename (highest demand)
2. imgcrush (visual feedback)
3. dirsnap (tree visualization)

**Deliverables**:
- Unified launcher app
- Drag-and-drop file selection
- Preview before execute
- Progress bars
- Basic settings

### Phase 2: Individual Tools (8 weeks)

**Goal**: Standalone apps for each tool.

**Week 5-6**: smartrename GUI
- File list view with checkboxes
- 6 rename modes as dropdown
- Live preview panel
- Undo button

**Week 7-8**: imgcrush GUI
- Image preview grid
- Quality slider
- Format conversion dropdown
- Before/after size comparison

**Week 9-10**: clipstack GUI
- Clipboard history list
- Search bar
- Pin toggle
- Copy button per entry

**Week 11-12**: dirsnap, envguard, quickmd GUIs
- dirsnap: Tree view widget, export options
- envguard: Vault list, add/get dialogs
- quickmd: Markdown editor preview

### Phase 3: Pro Features (4 weeks)

**Goal**: Premium GUI features.

**Features**:
- Dark mode
- Custom themes
- Keyboard shortcuts
- Batch operations queue
- Export reports
- History management
- Plugin system (future)

### Phase 4: Distribution (2 weeks)

**Goal**: Easy installation for non-developers.

**Platforms**:
- macOS: .app bundle via PyInstaller
- Windows: .exe installer
- Linux: .deb/.rpm packages

---

## 4. Resource Estimates

### Development

| Phase | Duration | Effort | Priority |
|-------|----------|--------|----------|
| Phase 1 MVP | 4 weeks | Full-time | High |
| Phase 2 Individual | 8 weeks | Full-time | High |
| Phase 3 Pro | 4 weeks | Part-time | Medium |
| Phase 4 Distribution | 2 weeks | Full-time | High |
| **Total** | **18 weeks** | - | - |

### Technical Requirements

- Python 3.9+
- PySide6 (~$0, open source)
- PyInstaller for bundling
- Design assets (icons, UI kit)
- CI/CD for GUI builds

---

## 5. GUI Feature Matrix

### smartrename GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| Preview | ✅ | ✅ | ✅ |
| 6 modes | ✅ | ✅ | ✅ |
| Undo | ✅ | ✅ | ✅ |
| Drag-drop | ❌ | ✅ | ✅ |
| File picker | ❌ | ✅ | ✅ |
| Regex builder | ⚠️ | ❌ | ✅ |
| Custom presets | ❌ | ❌ | ✅ |

### imgcrush GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| Compress | ✅ | ✅ | ✅ |
| Convert | ✅ | ✅ | ✅ |
| HEIC support | ✅ | ✅ | ✅ |
| Preview grid | ❌ | ✅ | ✅ |
| Quality slider | ⚠️ | ✅ | ✅ |
| Before/after | ❌ | ✅ | ✅ |
| Batch queue | ❌ | ❌ | ✅ |

### clipstack GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| History list | ✅ | ✅ | ✅ |
| Search | ✅ | ✅ | ✅ |
| Pin | ✅ | ✅ | ✅ |
| Auto-start | ✅ | ✅ | ✅ |
| Hotkey popup | ❌ | ❌ | ✅ |
| Categories | ❌ | ❌ | ✅ |

### dirsnap GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| Tree view | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ |
| Diff | ✅ | ✅ | ✅ |
| Interactive tree | ⚠️ | ✅ | ✅ |
| Save snapshots | ✅ | ✅ | ✅ |
| Visual diff | ❌ | ❌ | ✅ |

### envguard GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| Vault list | ✅ | ✅ | ✅ |
| Add/Get | ✅ | ✅ | ✅ |
| Scan | ✅ | ✅ | ✅ |
| Cloud sync | ✅ | ✅ | ✅ |
| Password manager UI | ❌ | ✅ | ✅ |
| Team sharing | ✅ | ⚠️ | ✅ |

### quickmd GUI

| Feature | CLI | GUI MVP | GUI Pro |
|---------|-----|---------|---------|
| Convert | ✅ | ✅ | ✅ |
| Templates | ✅ | ✅ | ✅ |
| Live preview | ✅ | ✅ | ✅ |
| Markdown editor | ❌ | ✅ | ✅ |
| PDF export | ✅ | ✅ | ✅ |
| Custom templates | ❌ | ❌ | ✅ |

---

## 6. Pricing Strategy

### Current Pricing (CLI)

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | Core features |
| Pro | $29 | All advanced |

### Proposed Pricing (CLI + GUI)

| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | CLI + Basic GUI |
| Pro | $29 | CLI + Full GUI |
| Team | $79 | Pro + 5 licenses + Team features |

**Bundle Discount**: GUI adds value but keeps same pricing to maintain goodwill.

---

## 7. Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| PySide6 bundle size | Large downloads | Offer web installer |
| Platform quirks | Bugs | Extensive testing on all platforms |
| Performance | Slow on old hardware | Optimize, offer Lite mode |
| Design quality | Poor UX | Hire UI designer or use templates |
| Maintenance burden | 2 codebases | Keep GUI thin, reuse CLI logic |
| User confusion | CLI vs GUI | Clear documentation, unified branding |

---

## 8. Success Metrics

### Phase 1 MVP

- Downloads: 1000+ (vs current CLI ~100)
- User feedback: 50+ responses
- GitHub stars: +50

### Phase 2 Individual

- Each tool downloads: 500+
- Pro conversions: +10%
- Support tickets: <20

### Phase 3 Pro

- Pro revenue: +$1000/month
- User retention: 70%+
- Feature requests: 20+

---

## 9. Next Steps

### Immediate (Week 1)

1. Set up PySide6 development environment
2. Create unified launcher prototype
3. Design UI mockups (Figma/Sketch)
4. Set up GUI CI/CD pipeline

### Decision Points

1. **Framework**: PySide6 vs CustomTkinter (decide by Week 2)
2. **MVP Scope**: 3 tools vs 6 tools (decide by Week 1)
3. **Designer**: Hire vs DIY (decide by Week 2)

---

## 10. Appendix: UI Mockup Concepts

### Unified Launcher (Home Screen)

```
┌─────────────────────────────────────────────┐
│  🛠️ macOS Tools Bundle                    ≡  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 📝      │ │ 🖼️      │ │ 📋      │       │
│  │ Rename  │ │ ImgCrush│ │ ClipStack│       │
│  │ Files   │ │ Images  │ │ History │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 🌳      │ │ 🔐      │ │ 📄      │       │
│  │ DirSnap │ │ EnvGuard│ │ QuickMD │       │
│  │ Tree    │ │ .env    │ │ Markdown│       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                             │
│  [Settings] [History] [Help]               │
└─────────────────────────────────────────────┘
```

### smartrename GUI

```
┌─────────────────────────────────────────────┐
│  📝 SmartRename                          ≡  │
├─────────────────────────────────────────────┤
│  [📁 Select Folder...]  ~/Downloads       │
│                                             │
│  Mode: [Sequence ▼]  Start: [001] Pad: [3] │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Preview (25 files)                    │ │
│  │ ───────────────────────────────────── │ │
│  │ image.jpg → 001_image.jpg            │ │
│  │ photo.png → 002_photo.png            │ │
│  │ doc.pdf  → 003_doc.pdf               │ │
│  │ ...                                   │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [Preview] [Execute] [Undo Last]           │
└─────────────────────────────────────────────┘
```

---

**Document Owner**: Francisezhang
**Last Updated**: 2026-04-25
**Next Review**: After MVP completion