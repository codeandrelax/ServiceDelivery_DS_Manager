Digital Signage Manager - DSM Software

# API - Service Delivery

## get_ad

URL: https://ds.manager.indigoingenium.ba/get_ad

Body:

```json
{
    "uuid": "d2:b7:06:c4:6f:5a"
}
```

Response:

```json
{
    "name": "Advertisement",
    "url": "http://indigoingenium.ba/Tuborg.mp4"
}
```

or

```json
{
    "name": "Redirection",
    "url": "http://www.ds.manager.indigoingenium.ba/register_device"
}
```

### Test

-- not added

## check_if_registered

URL: https://ds.manager.indigoingenium.ba/check_if_registered

Body:

```json
{
    "uuid": "d2:b7:06:c4:6f:5e"
}
```

Response:

```json
{
    "Redirect": "http://www.ds.manager.indigoingenium.ba/origin"
}
```

or

```json
{
    "Non-redirect": "Device not registered"
}
```

### Test

Insert display into DB:

```
INSERT INTO `displays` (`display_size`, `location_latitude`, `location_longitude`, `location_description`, `image`, `uuid`, `enabled`, `location_id`)
VALUES
(55.5, '40.7128N', '74.0060W', 'Located in the main office lobby.', 'image1.jpg', '00:14:22:01:23:45', TRUE, 1)
```

## report_focus

URL: https://ds.manager.indigoingenium.ba/report_focus

Body:

```json
{
    "uuid": "d2:b7:06:c4:6f:5e",
    "date": "2025-02-12T15:00:00Z",
    "is_in_focus": 1
}
```

Response:

```json
{
    "message": "Focus report successfully inserted"
}
```

or

```json
{
    "error": "Display not found"
}
```

- **400 Bad Request**: If the required fields (`uuid`, `date`, `is_in_focus`) are missing or incorrect.
- **404 Not Found**: If the `uuid` does not exist in the displays table.

# API - Backend

## get_uuids_by_user_id

Once client is logged in, populate next view with data obtained from this call - displayvise view.

URL: https://ds.manager.indigoingenium.ba/get_uuids_by_user_id

Body:

```json
{
    "user_id": 123
}
```

Response:

```json
{
    "uuids": [
        "00:14:22:01:23:45",
        "00:14:22:01:23:46",
        "00:14:22:01:23:47"
    ]
}
```

or

```json
{
    "error": "No UUIDs found for the given user_id"
}
```

### Test

Add users to db:

```
INSERT INTO `users` (`email`, `password`, `username`, `status`, `verified`, `resettable`, `roles_mask`, `registered`, `last_login`, `force_logout`)
VALUES
('testuser1@example.com', 'password123', 'testuser1', 1, 1, 1, 0, UNIX_TIMESTAMP(), NULL, 0),
('testuser2@example.com', 'password456', 'testuser2', 1, 1, 1, 0, UNIX_TIMESTAMP(), NULL, 0),
('testuser3@example.com', 'password789', 'testuser3', 1, 0, 1, 0, UNIX_TIMESTAMP(), NULL, 0);
```

Add displays to db:
```
INSERT INTO `displays` (`display_size`, `location_latitude`, `location_longitude`, `location_description`, `image`, `uuid`, `enabled`, `location_id`)
VALUES
(55.5, '40.7128N', '74.0060W', 'Located in the main office lobby.', 'image1.jpg', '00:14:22:01:23:45', TRUE, 1),
(42.0, '34.0522N', '118.2437W', 'In the warehouse near the entrance.', 'image2.jpg', '00:14:22:01:23:46', TRUE, 2),
(75.0, '51.5074N', '0.1278W', 'Display at the retail store entrance.', 'image3.jpg', '00:14:22:01:23:47', FALSE, 3);
```

Connect displays with users:

```
INSERT INTO `display_user` (`uuid`, `user_id`, `exclusive`, `exclusive_from`, `exclusive_to`)
VALUES
('00:14:22:01:23:45', 1, 0, NULL, NULL),
('00:14:22:01:23:45', 2, 0, NULL, NULL),
('00:14:22:01:23:45', 3, 0, NULL, NULL),
('00:14:22:01:23:45', 4, 0, NULL, NULL),
('00:14:22:01:23:45', 5, 0, NULL, NULL),
('00:14:22:01:23:45', 6, 0, NULL, NULL),

('00:14:22:01:23:46', 1, 0, NULL, NULL),
('00:14:22:01:23:46', 2, 0, NULL, NULL),
('00:14:22:01:23:46', 3, 0, NULL, NULL),
('00:14:22:01:23:46', 4, 0, NULL, NULL),
('00:14:22:01:23:46', 5, 0, NULL, NULL),
('00:14:22:01:23:46', 6, 0, NULL, NULL),

('00:14:22:01:23:47', 1, 0, NULL, NULL),
('00:14:22:01:23:47', 2, 0, NULL, NULL),
('00:14:22:01:23:47', 3, 0, NULL, NULL),
('00:14:22:01:23:47', 4, 0, NULL, NULL),
('00:14:22:01:23:47', 5, 0, NULL, NULL),
('00:14:22:01:23:47', 6, 0, NULL, NULL);
```

## get_user_info

URL: https://ds.manager.indigoingenium.ba/get_user_info

Body:

```json
{
  "email": "damjanovmail@gmail.com"
}
```

Response:

```json
{
    "id": 4,
    "email": "damjanovmail@gmail.com",
    "username": "damjan",
    "status": 0,
    "verified": 1,
    "resettable": 1,
    "roles_mask": 16,
    "registered": 1739313074,
    "last_login": 1739351696,
    "force_logout": 0,
    "phone_number": null
}
```

or

```json
{
    "error": "User not found"
}
```

### Test

```
INSERT INTO `users` (`email`, `password`, `username`, `status`, `verified`, `resettable`, `roles_mask`, `registered`, `last_login`, `force_logout`)
VALUES
('testuser1@example.com', 'password123', 'testuser1', 1, 1, 1, 0, UNIX_TIMESTAMP(), NULL, 0),
('testuser2@example.com', 'password456', 'testuser2', 1, 1, 1, 0, UNIX_TIMESTAMP(), NULL, 0),
('testuser3@example.com', 'password789', 'testuser3', 1, 0, 1, 0, UNIX_TIMESTAMP(), NULL, 0);
```

## get_display_config

URL: https://ds.manager.indigoingenium.ba/get_display_config

Body:

```json
{
    "uuid": "b1:a1:27:0f:31:01"
}
```

Response:

```json
{
    "brightness": 75,
    "contrast": 50,
    "saturation": 60,
    "hue": 30,
    "blur": 5,
    "grayscale": 0,
    "invert": 0,
    "sepia": 0,
    "opacity": 100
}
```

or

```json
{
    "error": "Display configuration not found"
}
```

### Test

Insert config into db:

```
INSERT INTO display_config (
    brightness, contrast, saturation, hue, blur, grayscale, invert, sepia, opacity, uuid
) 
VALUES (
    80, 70, 60, 45, 10, 0, 0, 0, 100, 'b1:a1:27:0f:31:01'
);
```

or update existing:

```
UPDATE display_config
SET 
    brightness = 100,
    contrast = 100,
    saturation = 50,
    hue = 0,
    blur = 0,
    grayscale = 0,
    invert = 0,
    sepia = 0,
    opacity = 100
WHERE uuid = 'b1:a1:27:0f:31:01';
```

## get_displays_filtered
## get_ad_list_for_display_per_uuid
## get_ad_list_for_display
## assign_ad_to_display
## remove_ad_from_display
## get_display_conditions
## insert_basic_condition
## insert_specific_condition
## get_all_basic_conditions
## register_new_display
## add_new_client
## remove_a_client
## get_visible_displays_per_client
## get_exclusive_displays_per_client
## get_currently_used_displays_per_client
## get_current_debt
## get_monthly_report
## set_display_enabled_to
## register_new_ad
## register_admin

This is done via Delight IM AUTH (php)
## register_client
Registering a client is done same as registering admin with one extra API call -> register_client
