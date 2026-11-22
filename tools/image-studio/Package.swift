// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "ImageStudio", platforms: [.macOS(.v13)], targets: [
    .target(name: "ImageImport"),
    .executableTarget(name: "ImageStudio", dependencies: ["ImageImport"]),
    .executableTarget(name: "ImageImportTests", dependencies: ["ImageImport"], path: "Tests/ImageImportTests")
], swiftLanguageModes: [.v5])
