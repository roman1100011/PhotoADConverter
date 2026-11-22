import CoreImage
import ImageIO
import UniformTypeIdentifiers

public struct ImportedImage {
    public let pixels: CIImage
    public let pages: Int

    public init(url: URL, page: Int = 0) throws {
        func failure(_ message: String) -> NSError {
            NSError(domain: "ImageImport", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
        }
        if url.pathExtension.lowercased() == "nef" {
            guard page == 0, let source = CGImageSourceCreateWithURL(url as CFURL, nil),
                  CGImageSourceGetCount(source) > 0,
                  let type = CGImageSourceGetType(source), UTType(type as String)?.conforms(to: .rawImage) == true,
                  let raw = CIRAWFilter(imageURL: url), let image = raw.outputImage else {
                throw failure("macOS could not decode this Nikon RAW file.")
            }
            pixels = image
            pages = 1
        } else {
            guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
                  let type = CGImageSourceGetType(source), type as String == UTType.tiff.identifier else {
                throw failure("Choose a readable TIFF or Nikon NEF file.")
            }
            pages = CGImageSourceGetCount(source)
            guard (0..<pages).contains(page), let image = CGImageSourceCreateImageAtIndex(source, page, nil) else {
                throw failure("Could not decode this TIFF page.")
            }
            let properties = CGImageSourceCopyPropertiesAtIndex(source, page, nil) as? [CFString: Any]
            pixels = CIImage(cgImage: image).oriented(forExifOrientation: properties?[kCGImagePropertyOrientation] as? Int32 ?? 1)
        }
    }

    public func preview(context: CIContext, exposure: Double) -> CGImage? {
        let scale = min(1, 2000 / max(pixels.extent.width, pixels.extent.height))
        let result = pixels.transformed(by: .init(scaleX: scale, y: scale))
            .applyingFilter("CIExposureAdjust", parameters: [kCIInputEVKey: exposure])
        return context.createCGImage(result, from: result.extent)
    }
}
