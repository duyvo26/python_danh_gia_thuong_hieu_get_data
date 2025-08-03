UPDATE `request_thuong_hieu_list`
SET `status` = 0, `google_html` = NULL
WHERE `google_html` LIKE '%CAPTCHA%';



SELECT * FROM `request_thuong_hieu_list` WHERE status = 0