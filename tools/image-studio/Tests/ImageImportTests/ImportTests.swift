import Foundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers
import ImageImport

func require<T>(_ value: T?) throws -> T {
    guard let value else { throw NSError(domain: "Import test", code: 1) }
    return value
}

@main
struct ImportTests {
    static func main() throws {
        try testMultipageTIFFAndPreview()
        try testInvalidNEF()
        if ProcessInfo.processInfo.environment["TEST_NEF"] != nil { try testCameraNEF() }
        print("Image import checks passed")
    }
    static func testMultipageTIFFAndPreview() throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".tiff")
        defer { try? FileManager.default.removeItem(at: url) }
        let dest = try require(CGImageDestinationCreateWithURL(url as CFURL, UTType.tiff.identifier as CFString, 2, nil))
        let context = CIContext(options: [.useSoftwareRenderer: true])
        for width in [20, 40] {
            let rect = CGRect(x: 0, y: 0, width: width, height: 10)
            let image = CIImage(color: .red).cropped(to: rect)
            CGImageDestinationAddImage(dest, try require(context.createCGImage(image, from: rect)), nil)
        }
        precondition(CGImageDestinationFinalize(dest))
        let second = try ImportedImage(url: url, page: 1)
        precondition(second.pages == 2)
        precondition(second.preview(context: context, exposure: 1)?.width == 40)
        precondition((try? ImportedImage(url: url, page: 2)) == nil)
    }

    static func testInvalidNEF() throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".nef")
        defer { try? FileManager.default.removeItem(at: url) }
        try Data("invalid".utf8).write(to: url)
        precondition((try? ImportedImage(url: url)) == nil)
    }

    static func testCameraNEF() throws {
        guard let path = ProcessInfo.processInfo.environment["TEST_NEF"] else {
            return
        }
        let image = try ImportedImage(url: URL(fileURLWithPath: path))
        let preview = try require(image.preview(context: CIContext(), exposure: 0))
        precondition(image.pixels.extent.width >= CGFloat(preview.width))
    }
}
