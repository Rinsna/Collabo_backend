# Influencer Approval System Documentation

## Overview
The influencer approval system ensures that only admin-approved influencers can access the platform. Companies and admins are not affected by this system.

## Features Implemented

### 1. Model Changes (User Model)
Added the following fields to the User model:

```python
# Boolean flag for quick approval check
is_approved = models.BooleanField(default=False)

# Detailed status tracking
approval_status = models.CharField(
    max_length=20, 
    choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
    default='approved'
)

# Audit trail
approved_at = models.DateTimeField(null=True, blank=True)
approved_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
rejection_reason = models.TextField(blank=True)
```

### 2. Automatic Status Assignment
- **New Influencer Registration**: Automatically set to `pending` status
- **Company/Admin Registration**: Automatically set to `approved` status
- **Existing Users**: Not affected (remain approved)

### 3. Login Restriction
Influencers with `pending` or `rejected` status cannot login:

```python
# Login validation in UserLoginSerializer
if user.user_type == 'influencer':
    if user.approval_status == 'pending':
        raise ValidationError('Your account is pending admin approval.')
    elif user.approval_status == 'rejected':
        raise ValidationError('Your account has been rejected. Please contact support.')
```

**Error Messages:**
- Pending: "Your account is pending admin approval."
- Rejected: "Your account has been rejected. Please contact support."

### 4. Admin API Endpoints

#### Get Pending Influencers
```
GET /api/accounts/admin/pending-influencers/
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "influencer@example.com",
    "username": "influencer1",
    "user_type": "influencer",
    "phone": "+1234567890",
    "approval_status": "pending",
    "created_at": "2026-02-11T10:00:00Z",
    "influencer_profile": {
      "bio": "Fashion influencer",
      "category": "fashion",
      "followers_count": 50000,
      ...
    }
  }
]
```

#### Get All Influencers (with filtering)
```
GET /api/accounts/admin/all-influencers/
GET /api/accounts/admin/all-influencers/?status=pending
GET /api/accounts/admin/all-influencers/?status=approved
GET /api/accounts/admin/all-influencers/?status=rejected
Authorization: Bearer <admin_token>
```

#### Approve Influencer
```
POST /api/accounts/admin/approve-influencer/<user_id>/
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Influencer approved successfully",
  "user": { ... }
}
```

#### Reject Influencer
```
POST /api/accounts/admin/reject-influencer/<user_id>/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "action": "reject",
  "rejection_reason": "Insufficient follower count"
}
```

**Response:**
```json
{
  "message": "Influencer rejected successfully",
  "user": { ... }
}
```

#### Bulk Approve Influencers
```
POST /api/accounts/admin/bulk-approve/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "message": "5 influencer(s) approved successfully",
  "approved_count": 5
}
```

#### Delete Influencer
```
DELETE /api/accounts/admin/delete-influencer/<user_id>/
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Influencer influencer1 deleted successfully"
}
```

#### Get Approval Statistics
```
GET /api/accounts/admin/approval-stats/
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "total_influencers": 150,
  "pending": 25,
  "approved": 120,
  "rejected": 5
}
```

### 5. Django Admin Panel Integration

#### Admin Actions
- **Approve selected influencers**: Bulk approve from admin panel
- **Reject selected influencers**: Bulk reject from admin panel

#### List Display
- Shows approval status in user list
- Filter by approval status
- Search by email/username

#### Edit Form
- Approval System section with all approval fields
- Read-only fields: approved_at, approved_by, created_at

## Usage Examples

### For Frontend Developers

#### 1. Handle Registration Response
```javascript
// Influencer registration
const response = await api.post('/api/accounts/register/', {
  email: 'influencer@example.com',
  username: 'influencer1',
  password: 'SecurePass123',
  password_confirm: 'SecurePass123',
  user_type: 'influencer',
  // ... other fields
});

// Show message to user
if (response.data.user.user_type === 'influencer') {
  showMessage('Registration successful! Your account is pending admin approval.');
}
```

#### 2. Handle Login Errors
```javascript
try {
  const response = await api.post('/api/accounts/login/', {
    email: 'influencer@example.com',
    password: 'SecurePass123'
  });
  // Login successful
} catch (error) {
  if (error.response?.data?.non_field_errors) {
    const message = error.response.data.non_field_errors[0];
    if (message.includes('pending admin approval')) {
      showError('Your account is awaiting admin approval. Please check back later.');
    } else if (message.includes('rejected')) {
      showError('Your account has been rejected. Please contact support.');
    }
  }
}
```

#### 3. Admin Dashboard - Pending Influencers
```javascript
// Fetch pending influencers
const response = await api.get('/api/accounts/admin/pending-influencers/', {
  headers: { Authorization: `Bearer ${adminToken}` }
});

// Display list with approve/reject buttons
response.data.forEach(influencer => {
  displayInfluencer(influencer, {
    onApprove: () => approveInfluencer(influencer.id),
    onReject: () => rejectInfluencer(influencer.id)
  });
});
```

#### 4. Approve Influencer
```javascript
async function approveInfluencer(userId) {
  try {
    const response = await api.post(
      `/api/accounts/admin/approve-influencer/${userId}/`,
      {},
      { headers: { Authorization: `Bearer ${adminToken}` } }
    );
    showSuccess(response.data.message);
    refreshList();
  } catch (error) {
    showError('Failed to approve influencer');
  }
}
```

#### 5. Reject Influencer
```javascript
async function rejectInfluencer(userId, reason) {
  try {
    const response = await api.post(
      `/api/accounts/admin/reject-influencer/${userId}/`,
      {
        action: 'reject',
        rejection_reason: reason
      },
      { headers: { Authorization: `Bearer ${adminToken}` } }
    );
    showSuccess(response.data.message);
    refreshList();
  } catch (error) {
    showError('Failed to reject influencer');
  }
}
```

## Security Considerations

1. **JWT Token Not Generated**: Unapproved influencers cannot get access tokens
2. **No Modification to Company Logic**: Companies login normally
3. **Admin-Only Endpoints**: All approval endpoints require `IsAdminUser` permission
4. **Audit Trail**: Tracks who approved and when
5. **Status Validation**: Double-check with both `is_approved` and `approval_status`

## Database Migration

Migration file created: `0013_user_approval_status_user_approved_at_and_more.py`

**To apply:**
```bash
python manage.py migrate
```

**To rollback (if needed):**
```bash
python manage.py migrate accounts 0012
```

## Testing Checklist

### Influencer Registration
- [ ] New influencer registers
- [ ] Status is set to `pending`
- [ ] `is_approved` is `False`
- [ ] Profile is created successfully

### Influencer Login (Pending)
- [ ] Pending influencer tries to login
- [ ] Receives error: "Your account is pending admin approval."
- [ ] No JWT token generated

### Influencer Login (Rejected)
- [ ] Rejected influencer tries to login
- [ ] Receives error: "Your account has been rejected. Please contact support."
- [ ] No JWT token generated

### Influencer Login (Approved)
- [ ] Approved influencer logs in successfully
- [ ] JWT token generated
- [ ] Can access protected endpoints

### Company Registration & Login
- [ ] Company registers
- [ ] Status is automatically `approved`
- [ ] Can login immediately
- [ ] No approval required

### Admin Approval
- [ ] Admin can view pending influencers
- [ ] Admin can approve influencer
- [ ] Influencer can now login
- [ ] `approved_at` and `approved_by` are set

### Admin Rejection
- [ ] Admin can reject influencer
- [ ] Rejection reason is saved
- [ ] Influencer cannot login

### Django Admin Panel
- [ ] Approval status visible in user list
- [ ] Can filter by approval status
- [ ] Bulk approve action works
- [ ] Bulk reject action works

## Troubleshooting

### Issue: Existing influencers cannot login
**Solution**: Run this command to approve all existing influencers:
```python
from accounts.models import User
User.objects.filter(user_type='influencer').update(
    is_approved=True, 
    approval_status='approved'
)
```

### Issue: Company cannot login
**Check**: Ensure company user_type is not 'influencer'
```python
user = User.objects.get(email='company@example.com')
print(user.user_type)  # Should be 'company'
print(user.is_approved)  # Should be True
```

### Issue: Admin endpoints return 403
**Check**: Ensure user is superuser
```python
user = User.objects.get(email='admin@example.com')
print(user.is_superuser)  # Should be True
print(user.is_staff)  # Should be True
```

## Future Enhancements

1. **Email Notifications**: Send email when approved/rejected
2. **Approval Comments**: Allow admins to add notes
3. **Auto-Approval Rules**: Approve based on follower count
4. **Appeal System**: Allow rejected influencers to appeal
5. **Approval Workflow**: Multi-step approval process
6. **Analytics Dashboard**: Track approval metrics over time

## API Summary

| Endpoint | Method | Permission | Description |
|----------|--------|------------|-------------|
| `/api/accounts/admin/pending-influencers/` | GET | Admin | List pending influencers |
| `/api/accounts/admin/all-influencers/` | GET | Admin | List all influencers |
| `/api/accounts/admin/approve-influencer/<id>/` | POST | Admin | Approve influencer |
| `/api/accounts/admin/reject-influencer/<id>/` | POST | Admin | Reject influencer |
| `/api/accounts/admin/bulk-approve/` | POST | Admin | Bulk approve |
| `/api/accounts/admin/delete-influencer/<id>/` | DELETE | Admin | Delete influencer |
| `/api/accounts/admin/approval-stats/` | GET | Admin | Get statistics |

## Support

For issues or questions, contact the development team or check the Django admin logs.
