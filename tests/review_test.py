import os
import sys
import json
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app.init import create_app
from app.db import db
from app.models import User, Instrument, Instru_ownership, Rental, Review

def test_reviews():
    """Comprehensive test suite for Reviews System based on Instru_ownership"""
    
    app = create_app()
    
    with app.app_context():
        # Clean database
        db.drop_all()
        db.create_all()
        
        print("\n" + "="*70)
        print("REVIEWS AND RATINGS SYSTEM TEST SUITE")
        print("="*70)
        
        tests_passed = 0
        tests_total = 0
        
        # TEST 1: Create test users
        tests_total += 1
        try:
            renter1 = User(
                email='renter1@test.com',
                name='John Renter',
                user_type='renter'
            )
            renter1.set_password('password123')
            
            renter2 = User(
                email='renter2@test.com',
                name='Jane Renter',
                user_type='renter'
            )
            renter2.set_password('password123')
            
            owner = User(
                email='owner@test.com',
                name='Bob Owner',
                user_type='owner'
            )
            owner.set_password('password123')
            
            db.session.add_all([renter1, renter2, owner])
            db.session.commit()
            
            print("✓ TEST 1: Create test users - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 1: Create test users - FAILED: {e}")
        
        # TEST 2: Create test instruments
        tests_total += 1
        try:
            guitar1 = Instrument(
                name='Acoustic Guitar',
                category='guitar',
                brand='Fender',
                model='Dreadnought'
            )
            guitar2 = Instrument(
                name='Acoustic Guitar',
                category='guitar',
                brand='Fender',
                model='Dreadnought'
            )
            piano = Instrument(
                name='Piano',
                category='keyboard',
                brand='Yamaha',
                model='P-125'
            )
            db.session.add_all([guitar1, guitar2, piano])
            db.session.commit()
            
            print("✓ TEST 2: Create test instruments - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 2: Create test instruments - FAILED: {e}")
        
        # TEST 3: Create instrument ownerships (owner has 2 guitars)
        tests_total += 1
        try:
            ownership1 = Instru_ownership(
                user_id=owner.id,
                instrument_id=guitar1.id,
                condition='good',
                daily_rate=25.0,
                location='Studio A'
            )
            ownership2 = Instru_ownership(
                user_id=owner.id,
                instrument_id=guitar2.id,
                condition='new',
                daily_rate=30.0,
                location='Studio B'
            )
            db.session.add_all([ownership1, ownership2])
            db.session.commit()
            
            print("✓ TEST 3: Create instrument ownerships (owner has 2 guitars) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 3: Create instrument ownerships - FAILED: {e}")
        
        # TEST 4: Create completed rentals
        tests_total += 1
        try:
            today = date.today()
            
            # Renter1 rents guitar1 (ownership1)
            rental1 = Rental(
                user_id=renter1.id,
                instru_ownership_id=ownership1.id,
                start_date=today - timedelta(days=10),
                end_date=today - timedelta(days=5),
                actual_return_date=today - timedelta(days=5),
                total_cost=125.0,
                status='completed'
            )
            
            # Renter2 rents guitar2 (ownership2)
            rental2 = Rental(
                user_id=renter2.id,
                instru_ownership_id=ownership2.id,
                start_date=today - timedelta(days=15),
                end_date=today - timedelta(days=8),
                actual_return_date=today - timedelta(days=8),
                total_cost=150.0,
                status='completed'
            )
            
            # Renter1 rents guitar2 again (ownership2)
            rental3 = Rental(
                user_id=renter1.id,
                instru_ownership_id=ownership2.id,
                start_date=today - timedelta(days=5),
                end_date=today - timedelta(days=2),
                actual_return_date=today - timedelta(days=2),
                total_cost=90.0,
                status='completed'
            )
            
            db.session.add_all([rental1, rental2, rental3])
            db.session.commit()
            
            print("✓ TEST 4: Create completed rentals - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 4: Create completed rentals - FAILED: {e}")
        
        # TEST 5: Create reviews for guitar1 (ownership1)
        tests_total += 1
        try:
            review1 = Review(
                rental_id=rental1.id,
                instru_ownership_id=ownership1.id,
                renter_id=renter1.id,
                rating=5,
                comment='Excellent guitar in perfect condition!'
            )
            db.session.add(review1)
            db.session.commit()
            
            print("✓ TEST 5: Create review for guitar1 - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 5: Create review for guitar1 - FAILED: {e}")
        
        # TEST 6: Create reviews for guitar2 (ownership2)
        tests_total += 1
        try:
            review2 = Review(
                rental_id=rental2.id,
                instru_ownership_id=ownership2.id,
                renter_id=renter2.id,
                rating=4,
                comment='Very good, minor scratch on body'
            )
            review3 = Review(
                rental_id=rental3.id,
                instru_ownership_id=ownership2.id,
                renter_id=renter1.id,
                rating=5,
                comment='Brand new condition, sounds amazing!'
            )
            db.session.add_all([review2, review3])
            db.session.commit()
            
            print("✓ TEST 6: Create multiple reviews for guitar2 - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 6: Create multiple reviews for guitar2 - FAILED: {e}")
        
        # TEST 7: Verify each guitar has its own review list
        tests_total += 1
        try:
            guitar1_reviews = Review.query.filter_by(instru_ownership_id=ownership1.id).all()
            guitar2_reviews = Review.query.filter_by(instru_ownership_id=ownership2.id).all()
            
            assert len(guitar1_reviews) == 1, f"Guitar1 should have 1 review, has {len(guitar1_reviews)}"
            assert len(guitar2_reviews) == 2, f"Guitar2 should have 2 reviews, has {len(guitar2_reviews)}"
            
            print("✓ TEST 7: Each guitar has its own review list - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 7: Each guitar has its own review list - FAILED: {e}")
        
        # TEST 8: Calculate average rating per ownership
        tests_total += 1
        try:
            from sqlalchemy import func
            
            avg_guitar1 = db.session.query(func.avg(Review.rating)).filter_by(
                instru_ownership_id=ownership1.id
            ).scalar()
            
            avg_guitar2 = db.session.query(func.avg(Review.rating)).filter_by(
                instru_ownership_id=ownership2.id
            ).scalar()
            
            assert float(avg_guitar1) == 5.0, f"Guitar1 avg should be 5.0, got {avg_guitar1}"
            assert float(avg_guitar2) == 4.5, f"Guitar2 avg should be 4.5, got {avg_guitar2}"
            
            print("✓ TEST 8: Calculate average rating per ownership - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 8: Calculate average rating per ownership - FAILED: {e}")
        
        # TEST 9: Verify unique constraint (one review per rental)
        tests_total += 1
        try:
            duplicate_review = Review(
                rental_id=rental1.id,
                instru_ownership_id=ownership1.id,
                renter_id=renter1.id,
                rating=3,
                comment='Duplicate'
            )
            db.session.add(duplicate_review)
            db.session.commit()
            
            print("✗ TEST 9: Verify unique constraint - FAILED: Should have raised error")
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e) or 'unique' in str(e).lower():
                print("✓ TEST 9: Verify unique constraint - PASSED")
                tests_passed += 1
            else:
                print(f"✗ TEST 9: Verify unique constraint - FAILED: {e}")
        
        # TEST 10: Verify review is linked to correct rental and ownership
        tests_total += 1
        try:
            fetched_review = Review.query.get(review1.id)
            
            assert fetched_review.rental_id == rental1.id, "Review not linked to rental"
            assert fetched_review.instru_ownership_id == ownership1.id, "Review not linked to ownership"
            assert fetched_review.renter_id == renter1.id, "Review renter_id mismatch"
            
            print("✓ TEST 10: Verify review relationships - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 10: Verify review relationships - FAILED: {e}")
        
        # TEST 11: Query reviews by ownership (what owner sees)
        tests_total += 1
        try:
            # Owner looks at guitar1
            guitar1_reviews = Review.query.filter_by(instru_ownership_id=ownership1.id).all()
            assert len(guitar1_reviews) == 1, "Guitar1 should have 1 review"
            
            # Owner looks at guitar2
            guitar2_reviews = Review.query.filter_by(instru_ownership_id=ownership2.id).all()
            assert len(guitar2_reviews) == 2, "Guitar2 should have 2 reviews"
            
            print("✓ TEST 11: Query reviews by ownership (owner view) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 11: Query reviews by ownership - FAILED: {e}")
        
        # TEST 12: Verify renter can see reviews of specific guitar they rented
        tests_total += 1
        try:
            # Renter1 rented guitar2 and can see reviews for that specific copy
            guitar2_reviews = Review.query.filter_by(instru_ownership_id=ownership2.id).all()
            renter_reviews = [r for r in guitar2_reviews if r.renter_id == renter1.id]
            
            assert len(renter_reviews) == 1, "Renter1 should have 1 review on guitar2"
            
            print("✓ TEST 12: Renter sees reviews of specific guitar - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ TEST 12: Renter sees reviews of specific guitar - FAILED: {e}")
        
        print("\n" + "="*70)
        print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
        print("="*70)
        
        if tests_passed == tests_total:
            print("\n✓ ALL REVIEW TESTS PASSED!")
        else:
            print(f"\n✗ {tests_total - tests_passed} test(s) failed")
            sys.exit(1)

if __name__ == '__main__':
    test_reviews()
