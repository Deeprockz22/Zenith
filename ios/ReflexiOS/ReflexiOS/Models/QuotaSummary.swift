import Foundation

public struct QuotaSummary: Codable, Hashable {
    public var date: String?
    public var episodesUsed: Int
    public var episodesMax: Int
    public var episodesRemaining: Int
    public var moviesUsed: Int
    public var moviesMax: Int
    public var moviesRemaining: Int
    public var episodesList: [WatchedItem]
    public var moviesList: [WatchedItem]
    
    enum CodingKeys: String, CodingKey {
        case date
        case episodesUsed = "episodes_used"
        case episodesMax = "episodes_max"
        case episodesRemaining = "episodes_remaining"
        case moviesUsed = "movies_used"
        case moviesMax = "movies_max"
        case moviesRemaining = "movies_remaining"
        case episodesList = "episodes_list"
        case moviesList = "movies_list"
    }
    
    public init(
        date: String? = nil,
        episodesUsed: Int = 0,
        episodesMax: Int = 2,
        episodesRemaining: Int = 2,
        moviesUsed: Int = 0,
        moviesMax: Int = 1,
        moviesRemaining: Int = 1,
        episodesList: [WatchedItem] = [],
        moviesList: [WatchedItem] = []
    ) {
        self.date = date
        self.episodesUsed = episodesUsed
        self.episodesMax = episodesMax
        self.episodesRemaining = episodesRemaining
        self.moviesUsed = moviesUsed
        self.moviesMax = moviesMax
        self.moviesRemaining = moviesRemaining
        self.episodesList = episodesList
        self.moviesList = moviesList
    }
    
    public static let sample = QuotaSummary(
        date: "2026-10-22",
        episodesUsed: 1,
        episodesMax: 2,
        episodesRemaining: 1,
        moviesUsed: 0,
        moviesMax: 1,
        moviesRemaining: 1,
        episodesList: [
            WatchedItem(title: "Severance S02E01 - Radical Honesty", timestamp: "13:20", mediaType: "series")
        ],
        moviesList: []
    )
}

public struct WatchedItem: Codable, Hashable, Identifiable {
    public var id: String { "\(timestamp ?? "")-\(title)" }
    public var title: String
    public var timestamp: String?
    public var mediaType: String?
    
    enum CodingKeys: String, CodingKey {
        case title
        case timestamp
        case mediaType = "media_type"
    }
    
    public init(title: String, timestamp: String? = nil, mediaType: String? = nil) {
        self.title = title
        self.timestamp = timestamp
        self.mediaType = mediaType
    }
}
