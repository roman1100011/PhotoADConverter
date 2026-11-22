import SwiftUI
import UniformTypeIdentifiers
import ImageImport
import CoreImage

@main
struct Studio: App {
    var body: some Scene { WindowGroup { Workspace() } }
}

struct Workspace: View {
    @State private var source: URL?
    @State private var image: ImportedImage?
    @State private var preview: CGImage?
    @State private var error = ""
    @State private var exposure = 0.0
    @State private var page = 0
    private static let context = CIContext()
    func render() {
        preview = image?.preview(context: Self.context, exposure: exposure)
        if preview == nil { error = "Could not render the selected image." }
    }
    func load(_ url: URL, index: Int) {
        do {
            let next = try ImportedImage(url: url, page: index)
            source = url
            image = next
            page = index
            exposure = 0
            error = ""
            render()
        } catch { self.error = error.localizedDescription }
    }
    var body: some View {
        HStack(spacing: 0) {
            ZStack {
                Color.black
                if let preview {
                    Image(decorative: preview, scale: 1).resizable().scaledToFit()
                } else { Text("Import a TIFF or NEF to preview it").foregroundColor(.white) }
            }.frame(maxWidth: .infinity, maxHeight: .infinity)
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Button("Import TIFF or NEF…") {
                        let panel = NSOpenPanel()
                        panel.allowedContentTypes = [.tiff, UTType(filenameExtension: "nef")!]
                        if panel.runModal() == .OK, let url = panel.url { load(url, index: 0) }
                    }
                    if let source, let image {
                        Text(source.lastPathComponent).bold()
                        Text("\(Int(image.pixels.extent.width)) × \(Int(image.pixels.extent.height)) px")
                        if image.pages > 1 {
                            Stepper("Page \(page + 1) of \(image.pages)", value: Binding(get: { page }, set: { load(source, index: $0) }), in: 0...(image.pages - 1))
                        }
                        Text("Exposure \(exposure, specifier: "%+.1f") EV")
                        Slider(value: $exposure, in: -3...3).onChange(of: exposure) { _ in render() }
                    }
                    if !error.isEmpty { Text(error).foregroundColor(.red) }
                }.padding()
            }.frame(width: 245)
        }.frame(minWidth: 740, minHeight: 460)
    }
}
