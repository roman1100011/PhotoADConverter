import Foundation
import CoreImage

do {
    let args = CommandLine.arguments
    guard args.count == 4, let page = Int(args[3]) else { exit(2) }
    let source = try ImportedImage(url: URL(fileURLWithPath: args[1]), page: page)
    try CIContext().writeTIFFRepresentation(of: source.pixels,
        to: URL(fileURLWithPath: args[2]), format: .RGBA16,
        colorSpace: CGColorSpace(name: CGColorSpace.linearSRGB)!)
    print(source.pages)
} catch {
    FileHandle.standardError.write(Data(error.localizedDescription.utf8))
    exit(1)
}
