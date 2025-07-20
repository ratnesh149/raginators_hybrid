# Experience-Based Sorting Enhancement

## Overview
Updated the candidate shortlisting system to properly handle experience-based sorting by considering both minimum and maximum experience values, not just minimum values.

## Changes Made

### 1. Enhanced Candidate Shortlist Tool (`tools/candidate_shortlist.py`)

#### New Combined Scoring Algorithm
- **Previous**: Only used vector similarity scores for ranking
- **Updated**: Combines multiple factors for better candidate ranking:
  - **60%** - Vector similarity match score
  - **30%** - Experience level preference within range
  - **10%** - Technology skills boost

#### Experience-Based Sorting Logic
```python
def _calculate_combined_score(self, candidate, min_experience, max_experience):
    # For open-ended ranges (e.g., 10+ years)
    if max_experience == 999:
        experience_score = min(1.0, candidate_experience / (min_experience + 10))
    
    # For closed ranges (e.g., 3-5 years)
    else:
        normalized_exp = (candidate_experience - min_experience) / range_size
        experience_score = normalized_exp
```

#### Key Improvements

1. **Proper Range Handling**:
   - Entry Level (0-2 years): Prefers candidates closer to 2 years
   - Mid Level (3-5 years): Prefers candidates closer to 5 years  
   - Senior Level (6-10 years): Prefers candidates closer to 10 years
   - Expert Level (10+ years): Prefers candidates with more experience

2. **Enhanced Sorting**:
   - Candidates are now sorted by combined score (not just similarity)
   - Higher experience within range gets better ranking
   - Technology skills provide additional boost

3. **Better Display**:
   - Shows combined score with breakdown
   - Indicates experience-based ranking
   - Provides experience distribution in summary

### 2. Updated Result Formatting

#### Before:
```
📊 Match Score: 0.75/1.00
⭐ HIGHLY RECOMMENDED
```

#### After:
```
📊 Combined Score: 0.82/1.00 (Match: 0.75 + Experience Rank)
⭐ HIGHLY RECOMMENDED (Top experience + match)
```

### 3. Enhanced Summary Statistics

#### New Metrics:
- Combined score distribution (>80%, 60-80%)
- Experience distribution by range
- Experience-optimized ranking confirmation
- Detailed scoring methodology explanation

## Usage Examples

### Entry Level Search
```python
shortlist_tool._run(
    job_requirements="Frontend developer with React",
    min_experience=0,
    max_experience=2,
    n_candidates=5
)
```
**Result**: Candidates with 0-2 years, ranked with preference for those closer to 2 years

### Senior Level Search  
```python
shortlist_tool._run(
    job_requirements="Frontend developer with React",
    min_experience=6,
    max_experience=10,
    n_candidates=5
)
```
**Result**: Candidates with 6-10 years, ranked with preference for those closer to 10 years

### Expert Level Search
```python
shortlist_tool._run(
    job_requirements="Frontend developer with React", 
    min_experience=10,
    max_experience=999,
    n_candidates=5
)
```
**Result**: Candidates with 10+ years, ranked with preference for higher experience

## Testing

Run the test script to verify functionality:
```bash
python test_experience_sorting.py
```

## Benefits

1. **More Accurate Ranking**: Combines similarity and experience preferences
2. **Better User Experience**: Shows why candidates are ranked in specific order
3. **Flexible Ranges**: Handles both closed ranges (3-5 years) and open ranges (10+ years)
4. **Transparent Scoring**: Users can see how scores are calculated
5. **Experience Distribution**: Shows spread of experience levels in results

## Backward Compatibility

- All existing API calls continue to work
- Default behavior (min_experience=0, max_experience=999) unchanged
- Enhanced features are additive, not breaking changes

## Future Enhancements

1. **Configurable Weights**: Allow users to adjust scoring weights
2. **Industry-Specific Scoring**: Different weights for different job types
3. **Location-Based Scoring**: Factor in geographic preferences
4. **Salary Range Matching**: Include compensation expectations in scoring
