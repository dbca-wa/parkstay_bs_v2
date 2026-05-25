# Plan: Park-level Custom Acknowledgment Checkbox

## Summary

Remove the hardcoded "I understand the facilities..." (`trav_res`) checkbox from the booking page.
Replace it with a park-configurable acknowledgment checkbox: if a `Park` record has text in
`custom_acknowledgment`, that text is shown as a required checkbox before the user can proceed.
Blank means no extra checkbox is shown. This is generic — any park can have any wording in future
(e.g. Dirk Hartog Island barge booking requirement).

The existing `trav_res` value continues to be saved in `booking.details` for historical tracking
consistency (via a hidden form field, always `true`).

---

## Steps

### Phase 1: Model + Migration

1. **`parkstay/models.py`** — Add to `Park` model:
   ```python
   custom_acknowledgment = models.TextField(
       blank=True, default='',
       help_text='If set, users must check this acknowledgment before proceeding with a booking.'
   )
   ```

2. **`parkstay/migrations/0154_park_custom_acknowledgment.py`** — Create manually:
   ```python
   from django.db import migrations, models

   class Migration(migrations.Migration):
       dependencies = [('parkstay', '0153_bulkrefundcancellist_completed')]
       operations = [
           migrations.AddField(
               model_name='park',
               name='custom_acknowledgment',
               field=models.TextField(
                   blank=True, default='',
                   help_text='If set, users must check this acknowledgment before proceeding with a booking.'
               ),
           ),
       ]
   ```

### Phase 2: Admin

3. **`parkstay/admin.py`** — No changes required. Django auto-includes all model fields in the
   edit form. `ParkAdmin` will show `custom_acknowledgment` automatically.

### Phase 3: View

4. **`parkstay/views.py`** (`render_page`) — Add `custom_acknowledgment` to the template context
   immediately before the `return render(...)` call:
   ```python
   custom_acknowledgment = booking.campground.park.custom_acknowledgment if booking else ''
   ```
   And include it in the `return render(...)` dict:
   ```python
   'custom_acknowledgment': custom_acknowledgment,
   ```

5. **`parkstay/views.py`** (`post`) — Add one line alongside the other `booking.details` saves:
   ```python
   booking.details['custom_acknowledgment'] = request.POST.get('custom_acknowledgment', False)
   ```

### Phase 4: Template (`make_booking.html`)

6. **Remove** the `trav_res` checkbox `<div class="checkbox">` block (lines ~781–783).
   Replace with a hidden input so `trav_res` continues to be stored in `booking.details`:
   ```html
   <input type="hidden" name="trav_res" value="true">
   ```

7. **Add** the conditional acknowledgment checkbox immediately after the `toc` checkbox div:
   ```html
   {% if custom_acknowledgment %}
   <div class="checkbox">
       <label>
           <input type="checkbox" name="custom_acknowledgment"
                  v-model="custom_acknowledgment_checked">
           {{ custom_acknowledgment }}
       </label>
   </div>
   {% endif %}
   ```

8. **Vue data** — In the `data:` block (line ~940):
   - Remove: `trav_res: false,`
   - Add:
     ```javascript
     has_custom_acknowledgment: {% if custom_acknowledgment %}true{% else %}false{% endif %},
     custom_acknowledgment_checked: false,
     ```

9. **PROCEED button** — Update the `:disabled` binding (line ~785):
   ```html
   <!-- Before -->
   :disabled="!toc||!trav_res"
   <!-- After -->
   :disabled="!toc || (has_custom_acknowledgment && !custom_acknowledgment_checked)"
   ```

---

## Affected Files

| File | Change |
|---|---|
| `parkstay/models.py` | Add `custom_acknowledgment` field to `Park` |
| `parkstay/migrations/0154_park_custom_acknowledgment.py` | New migration |
| `parkstay/admin.py` | No change |
| `parkstay/views.py` | Pass `custom_acknowledgment` in context; save to `booking.details` |
| `parkstay/templates/ps/booking/make_booking.html` | Replace checkbox, update Vue data and PROCEED condition |

---

## Verification Checklist

1. `python manage.py migrate` — runs without error
2. Django admin: open any Park — `Custom acknowledgment` text field is visible and saves correctly
3. Park with `custom_acknowledgment = ""` (default): no extra checkbox shown; PROCEED enabled with `toc` only
4. Park with `custom_acknowledgment = "I acknowledge..."`: that text shown as a checkbox; PROCEED blocked until checked
5. After booking confirmation: `booking.details` contains both `trav_res: 'true'` and `custom_acknowledgment: 'true'`

---

## Decisions & Out of Scope

- **Generic over specific**: field is plain text, not a boolean flag — any park can use any wording
- **`trav_res` preserved**: hidden input always submits `true` — no disruption to existing tracking
- **No server-side validation**: consistent with how `toc` and `trav_res` are currently handled
- **Single extra checkbox only**: multiple additional checkboxes per park are out of scope
