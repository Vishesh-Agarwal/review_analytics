export interface Review {
  reviewId: string;
  userName: string;
  content: string;
  score: number;
  thumbsUpCount: number;
  reviewCreatedVersion: string;
  commentedAt: string; // ISO 8601 date string
}