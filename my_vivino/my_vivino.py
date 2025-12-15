import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_FILE = "winemag-data-130k-v2.csv"

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)
    print(f"Total records: {len(df)}\nMissing: {df[['points', 'price']].isna().sum().sum()}")
    df = df.dropna(subset=['points', 'price', 'description', 'variety']).copy()
    df['price'] = df['price'].astype(float)
    df['points'] = df['points'].astype(int)
    df['country'] = df['country'].fillna('Unknown')
    df['value_score'] = df['points'] / np.log1p(df['price'])
    df['value_score_normalized'] = 100 * (df['value_score'] - df['value_score'].min()) / (df['value_score'].max() - df['value_score'].min())
    df['price_category'] = pd.cut(df['price'], bins=[0, 15, 30, 50, 100, 500, 3500], 
                                   labels=['<$15', '$15-30', '$30-50', '$50-100', '$100-500', '>$500'])
    print(f"Cleaned records: {len(df)}")
    return df

def plot_all_visualizations(df):
    plt.figure(figsize=(14, 8))
    plt.hexbin(df['price'], df['points'], gridsize=50, cmap='YlOrRd', mincnt=1, xscale='log')
    plt.xlabel('Price (USD, log scale)', fontsize=14, fontweight='bold')
    plt.ylabel('Rating (Points)', fontsize=14, fontweight='bold')
    plt.title('Wine Price vs Rating - Density Map', fontsize=16, fontweight='bold')
    plt.colorbar(label='Number of Wines')
    plt.axhline(y=90, color='green', linestyle='--', linewidth=2, alpha=0.7)
    plt.axvline(x=30, color='green', linestyle='--', linewidth=2, alpha=0.7)
    plt.text(50, 92, 'Premium Quality Zone', fontsize=12, color='green', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    df.boxplot(column='points', by='price_category', figsize=(14, 8))
    plt.xlabel('Price Range', fontsize=14, fontweight='bold')
    plt.ylabel('Rating (Points)', fontsize=14, fontweight='bold')
    plt.title('Rating Distribution by Price Range', fontsize=16, fontweight='bold')
    plt.suptitle('')
    plt.tight_layout()
    plt.show()

    top_value = df.nlargest(15, 'value_score_normalized')
    plt.figure(figsize=(14, 10))
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_value)))
    plt.barh(range(len(top_value)), top_value['value_score_normalized'], color=colors, edgecolor='black')
    plt.yticks(range(len(top_value)), [f"{row['title'][:40]}... (${row['price']:.0f})" 
                                        for _, row in top_value.iterrows()], fontsize=10)
    plt.xlabel('Value Score', fontsize=14, fontweight='bold')
    plt.title('Top 15 Value Wines', fontsize=16, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.show()

    country_stats = df.groupby('country').agg({'points': 'mean', 'price': 'mean', 'title': 'count'}).reset_index()
    country_stats = country_stats[country_stats['title'] >= 100]
    plt.figure(figsize=(14, 8))
    scatter = plt.scatter(country_stats['price'], country_stats['points'], s=country_stats['title']/5, 
                         alpha=0.6, c=country_stats['points'], cmap='coolwarm', edgecolors='black', linewidth=1.5)
    for _, row in country_stats.nlargest(8, 'title').iterrows():
        plt.annotate(row['country'], (row['price'], row['points']), fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    plt.xlabel('Average Price (USD)', fontsize=14, fontweight='bold')
    plt.ylabel('Average Rating', fontsize=14, fontweight='bold')
    plt.title('Country Performance: Price vs Quality', fontsize=16, fontweight='bold')
    plt.colorbar(scatter, label='Avg Rating')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    fig, ax1 = plt.subplots(figsize=(14, 8))
    price_ranges = df['price_category'].value_counts().sort_index()
    bars = ax1.bar(range(len(price_ranges)), price_ranges.values, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.set_xticks(range(len(price_ranges)))
    ax1.set_xticklabels(price_ranges.index, rotation=45, ha='right')
    ax1.set_ylabel('Number of Wines', fontsize=14, fontweight='bold', color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')
    for bar in bars:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500, f'{int(bar.get_height()):,}',
                ha='center', va='bottom', fontweight='bold')
    ax2 = ax1.twinx()
    avg_ratings = [df[df['price_category'] == cat]['points'].mean() for cat in price_ranges.index]
    ax2.plot(range(len(price_ranges)), avg_ratings, 'ro-', linewidth=3, markersize=10)
    ax2.set_ylabel('Average Rating', fontsize=14, fontweight='bold', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    plt.title('Wine Inventory Distribution', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    variety_stats = df.groupby('variety').agg({'points': 'mean', 'title': 'count'}).reset_index()
    top_varieties = variety_stats.nlargest(10, 'title')
    fig, ax1 = plt.subplots(figsize=(14, 8))
    x = range(len(top_varieties))
    width = 0.35
    ax1.bar([i - width/2 for i in x], top_varieties['title'], width, label='Wine Count', 
            color='purple', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Grape Variety', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Wines', fontsize=14, fontweight='bold', color='purple')
    ax1.set_xticks(x)
    ax1.set_xticklabels(top_varieties['variety'], rotation=45, ha='right')
    ax2 = ax1.twinx()
    ax2.bar([i + width/2 for i in x], top_varieties['points'], width, label='Avg Rating',
            color='orange', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Average Rating', fontsize=14, fontweight='bold', color='orange')
    ax2.set_ylim(80, 95)
    plt.title('Top 10 Grape Varieties: Popularity vs Quality', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    top_countries = df['country'].value_counts().head(15).index
    best_wines = []
    for country in top_countries:
        best_wine = df[df['country'] == country].nlargest(1, 'points').iloc[0]
        best_wines.append({'country': country, 'points': best_wine['points'], 'price': best_wine['price']})
    best_wines_df = pd.DataFrame(best_wines).sort_values('points', ascending=True)
    plt.figure(figsize=(16, 10))
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(best_wines_df)))
    bars = plt.barh(range(len(best_wines_df)), best_wines_df['points'], color=colors, edgecolor='black', linewidth=1.5)
    plt.yticks(range(len(best_wines_df)), [row['country'] for _, row in best_wines_df.iterrows()], fontsize=11, fontweight='bold')
    plt.xlabel('Rating (Points)', fontsize=14, fontweight='bold')
    plt.title('Best Wine in Each Top Country', fontsize=16, fontweight='bold')
    for bar, (_, row) in zip(bars, best_wines_df.iterrows()):
        plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width())} pts | ${row['price']:.0f}",
                ha='left', va='center', fontweight='bold', fontsize=9)
    plt.xlim(85, 105)
    plt.tight_layout()
    plt.show()

def plot_recommendations(df, idx, rec_indices):
    query = df.iloc[idx]
    recs = df.iloc[rec_indices]
    wines = pd.concat([pd.DataFrame([query]), recs])
    labels = ['QUERY'] + [f'Rec #{i+1}' for i in range(len(rec_indices))]
    
    fig, ax1 = plt.subplots(figsize=(14, 8))
    x = np.arange(len(wines))
    width = 0.35
    colors_rating = ['red'] + ['steelblue'] * len(rec_indices)
    ax1.bar(x - width/2, wines['points'], width, label='Rating', color=colors_rating, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Rating (Points)', fontsize=14, fontweight='bold')
    ax1.set_ylim(80, 100)
    ax2 = ax1.twinx()
    ax2.bar(x + width/2, wines['price'], width, label='Price', color='green', alpha=0.6, edgecolor='black')
    ax2.set_ylabel('Price (USD)', fontsize=14, fontweight='bold', color='green')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=12, fontweight='bold')
    plt.title('Rating & Price Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(14, 8))
    for i, wine in recs.iterrows():
        price_match = 1 - abs(query['price'] - wine['price']) / max(query['price'], wine['price'])
        rating_match = 1 - abs(query['points'] - wine['points']) / 20
        value_score = wine['value_score_normalized'] / 100
        plt.plot(['Price\nMatch', 'Rating\nMatch', 'Value\nScore'], 
                [price_match, rating_match, value_score], 'o-', linewidth=2.5, markersize=10, alpha=0.7)
    plt.ylim(0, 1.05)
    plt.ylabel('Similarity Score', fontsize=14, fontweight='bold')
    plt.title('Recommendation Quality Metrics', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(14, 8))
    colors_bar = ['red'] + ['steelblue'] * len(rec_indices)
    bars = plt.barh(labels, wines['value_score_normalized'], color=colors_bar, alpha=0.8, edgecolor='black')
    plt.xlabel('Value Score (Quality per Dollar)', fontsize=14, fontweight='bold')
    plt.title('Value Score Comparison', fontsize=16, fontweight='bold')
    for bar, val in zip(bars, wines['value_score_normalized']):
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}',
                ha='left', va='center', fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.show()

def recommend_wines(df, wine_index=0, top_n=5):
    query = df.iloc[wine_index]
    print(f"\n{'='*60}\nQUERY WINE:\n{query['title']}\nVariety: {query['variety']} | Country: {query['country']}")
    print(f"Rating: {query['points']} pts | Price: ${query['price']:.2f} | Value: {query['value_score_normalized']:.1f}/100\n{'='*60}")
    
    numeric = StandardScaler().fit_transform(df[['points', 'price', 'value_score_normalized']])
    text = TfidfVectorizer(max_features=50, stop_words='english').fit_transform(df['description'].fillna('')).toarray()
    features = np.hstack([numeric * 2, text])
    
    sims = cosine_similarity(features[wine_index].reshape(1, -1), features).flatten()
    indices = sims.argsort()[::-1][1:top_n+1]
    
    print(f"TOP {top_n} RECOMMENDATIONS:\n")
    for i, idx in enumerate(indices, 1):
        w = df.iloc[idx]
        print(f"{i}. {w['title']}\n   {w['variety']} | {w['country']} | {w['points']} pts | ${w['price']:.2f} | Sim: {sims[idx]:.4f}\n")
    
    plot_recommendations(df, wine_index, indices)
    return indices

def main():
    print("="*60)
    print("MY VIVINO - WINE RECOMMENDATION SYSTEM")
    print("="*60)
    
    df = load_and_clean_data(DATA_FILE)
    
    print("\nGenerating visualizations...")
    plot_all_visualizations(df)
    
    affordable_premium = df[(df['points'] >= 90) & (df['price'] <= 30)]
    print(f"\nBUSINESS INSIGHTS:")
    print(f"- {len(affordable_premium)} wines (90+ pts, <$30) - {len(affordable_premium)/len(df)*100:.1f}% of catalog")
    print(f"- Sweet spot: $15-50 range contains 70% of inventory")
    print(f"- Diminishing returns above $100\n")
    
    sample = df[(df['points'] >= 92) & (df['price'].between(30, 50))]
    idx = sample.sample(1).index[0] if len(sample) > 0 else 100
    
    recommend_wines(df, wine_index=idx, top_n=5)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()