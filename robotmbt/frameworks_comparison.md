# RobotMBT Visualization Framework Analysis

## Framework Comparison

| Feature | Plotly | Bokeh | NetworkX |
|---------|---------|--------|-----------|
| **Graph Structure Visualization** | ✅ Excellent interactive network graphs with hover details | ✅ Good network graphs but needs more setup | ❌ Only basic static diagrams |
| **Path Highlighting** | ✅ Easy to color nodes and edges to show executed vs uncovered paths | ✅ Possible but requires manual styling work | ❌ Limited highlighting capabilities |
| **User Interaction** | ✅ Built-in zoom, pan, hover with custom tooltips showing scenario details | ✅ Interactive but needs custom code for advanced features | ❌ No native interactivity |
| **HTML Report Integration** | ✅ Direct embedding in Robot Framework HTML reports | ✅ https://docs.bokeh.org/en/2.4.3/docs/user_guide/embed.html | ❌ Static images only |
| **Export Options** | ✅ One-click export to PNG, SVG, PDF, HTML | 🟨 Requires `selenium` https://docs.bokeh.org/en/2.4.3/docs/user_guide/export.html  | ❌ Limited to basic image formats |
| **Quantitative Metrics Display** | ✅ Can show coverage stats, node counts, and trace data alongside graph | ✅ Possible but needs more development effort | ✅ Good for calculating metrics, poor for display |
| **Automatic Generation** | ✅ Fits into RobotMBT's post-processing workflow, high-level API, quick prototyping | 🟨 Requires more integration work, needed for polished results | ❌ Not designed for automated reporting and modern visualization |

## How Plotly Meets Project Requirements

### Must Have Requirements
1. **Graph of all scenarios** - Plotly's network graphs clearly show scenarios as nodes and relationships as edges
2. **Handle repetition** - Node size/color can show repetition counts; edge thickness can indicate transition frequency  
3. **Differentiate executed path** - Easy color coding (green for executed, gray for uncovered) with Plotly's styling
4. **Quantitative information** - Plotly can display metrics panels alongside the graph showing coverage percentages
5. **Clear node/edge identification** - Hover tooltips show scenario names and relationship details
6. **Coverage indication** - Color coding and side metrics show how much of the model was exercised
7. **Legend/explanation** - Plotly annotations and side panels provide necessary documentation

### Should Have Requirements  
1. **Automatic generation** - Plotly HTML files generate automatically after test runs, which fits into Robot Framework workflow

### Could Have Requirements
1. **Interactive exploration** - Built-in zoom, pan, and hover satisfy basic interaction needs
2. **Filtering capabilities** - Plotly's buttons and sliders can implement show/hide functionality
3. **Export options** - Native support for PNG, SVG, PDF, and HTML export
4. **Test run information** - Side panels can display seed values, runtime, and other metadata

## Recommendation: Plotly + NetworkX

**Technical Benefits:**
- Uses existing `suitedata.py` structures (Suite, Scenario, Step) for data extraction
- Integrates with RobotMBT's `TraceState` from `tracestate.py` to track executed paths  
- Leverages NetworkX for graph calculations while using Plotly for visualization
- Generates HTML that embeds directly into Robot Framework's reporting system

**User Experience Benefits:**
- Users can immediately explore scenario relationships without learning new tools
- The visualization helps validate model correctness by showing unexpected connections
- Coverage metrics help teams understand test completeness at a glance
- The interactive nature supports both high-level overview and detailed investigation

## Implementation Approach

The prototype uses:
- `ModelVisualizer` class to process RobotMBT suite data
- NetworkX for graph structure and path calculations  
- Plotly for interactive visualization generation
- Integration with `SuiteReplacer` in `suitereplacer.py` for automatic post-run generation
