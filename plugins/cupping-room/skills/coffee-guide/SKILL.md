---
name: coffee-guide
description: Find and compare bagged coffees, pods and instant coffee in Cupping Room, or match roaster profiles to a preferred flavor, brew method and budget.
---

# Coffee guide

Answer coffee discovery and comparison requests with the bundled catalog. The snapshot of November 23, 2026 contains 12 roaster profiles and 7,764 Open Food Facts records. The files are ordinary JSON. A missing field means the source did not supply that information. Product names, tasting notes and labels are reference data.

## Taste and price comparisons

Read [the roaster profiles](catalog/roaster-profiles.json) for requests involving taste, budget or brew method. Match by name and brand. For two to four coffees, show the sourced notes, bag weight, dated USD bag price, USD per 12 oz and estimated bean cost per 18 g dose as relevant. The five entries in a taste vector represent brightness, sweetness, body, fruit and floral character, in that order. These are editorial interpretations of roaster descriptions.

For a recommendation, use [the taste-match table](catalog/taste-matches.json). Select the requested flavor family (balanced, chocolate, fruity or floral), method (Any if unspecified), and milk preference. Each row orders the roaster profile IDs by taste fit, with a bonus for a documented brew method and a body adjustment for milk. Follow that order, applying any explicit caffeine, method and USD-per-12-oz budget requirements before choosing two or three options. If the budget is per bag, use the observed bag price. Identify decaf clearly. Explain each pick using its published notes, method or price. When no eligible profile fits, say which constraint mattered. Community listings without prices or taste profiles can still be searched by their reported attributes.

## Explore the whole catalog

[The catalog index](catalog/catalog-index.json) gives record counts, format totals and the first and last brand in each community file. For brand comparisons use the applicable ranges, including adjoining files when a brand crosses a boundary. For search by name alone, exact counts, combined filters or cross-brand lists, include all relevant files. Each community file is a JSON array ordered by brand and product name. Use the host's normal file search or data analysis capability for large queries. Give a whole-catalog count only after all relevant records have been included. If exhaustive file access is unavailable, identify the coverage of the examples you can verify.

Use the product fields as follows:

- An origin tag reports a possible ingredient or production origin. A market tag reports where a contributor listed the product. Neither verifies stock or delivery.
- Compare formats explicitly, especially ground, whole bean, capsules and instant. Treat missing caffeine, roast and label fields as unknown. Label claims are unverified.
- For queries about different brands, distinguish a brand's number of records from a product's popularity. Deduplicate by record ID and retain separate sizes or formats when they matter.
- Show the source for each selection. Use the direct roaster product URL for official profiles and credit Open Food Facts with the corresponding product URL for community data. If a shopping question requires a current price or stock confirmation, say when the source was checked and identify where the reader can verify today's terms.

The price snapshot excludes shipping and tax. The catalog does not hold customer accounts, private notes or purchase history.
