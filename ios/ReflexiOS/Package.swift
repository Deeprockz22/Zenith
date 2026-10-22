// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ReflexiOS",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "ReflexiOS",
            targets: ["ReflexiOS"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "ReflexiOS",
            path: "ReflexiOS",
            exclude: ["Info.plist", "Assets.xcassets"]
        ),
    ]
)
