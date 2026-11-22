# Architecture and next milestones

## Requirements

- Launch as a regular desktop application with a basic UI and no command-line use.
- Import scanned film negatives and invert them to positive images.
- Select a region containing an 18% gray reference for white balance.
- Adjust shadow and highlight hue and saturation independently.
- Adjust luminance, exposure and black point; display an image histogram.
- Use Python primarily, native C/C++ libraries for expensive calculations, and no Java.

## Boundaries

`ui` owns widgets and user interaction. `processing` owns pixel math and must not
depend on Qt widgets. `imaging` will own file decoding, export, metadata and color
profile handling. Keep source pixels immutable and store edit parameters
separately so previews and exports can use the same pipeline.

Use NumPy vectorized operations and OpenCV native kernels. Do not implement
per-pixel Python loops. Profile before adding custom C++ extensions; add CMake and
bindings only if existing native kernels cannot handle a measured bottleneck.
OpenCV is the headless distribution to avoid competing GUI frameworks with Qt.

Before editing is implemented, define the internal color space and channel order
(RGB; OpenCV adapters must convert BGR explicitly). Preserve 16-bit scan precision,
use floating-point working data, and distinguish linear luminance from encoded
display values. OpenCV alone is not an ICC color-management solution; select an
ICC-aware adapter before color-critical import/export is released.

An 18% gray reference provides a neutral target for channel balance. Its linear
luminance is not the display-encoded value 0.18. Keep white balance neutralization
separate from exposure calibration; define whether selection is sampled before or
after negative conversion when implementing the pipeline. Color negative inversion
also needs film-base/orange-mask handling, beyond simply subtracting from white.

Heavy processing must run outside UI event handlers, with reduced-resolution
previews and cancellation of obsolete jobs. Histogram and export must use clearly
defined processing stages. Implement these policies with the image pipeline;
the current shell contains no image operations beyond the native dependency smoke check.

## Milestones

1. Foundation: package layout, environment, Qt shell and local desktop bundle.
2. Image import: 16-bit TIFF support, metadata, color-management policy and zoomable preview.
3. Conversion: negative inversion and film-base handling, selected gray-region white balance.
4. Controls: exposure, black point, luminance, shadow/highlight hue and saturation, histogram.
5. Output: full-resolution export, saved edit parameters and responsive background processing.
6. Release: reference-image validation, packaging licenses, icon, signing/notarization and installers.
