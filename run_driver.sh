#!/bin/bash

# to export env variables
set -a
. ./local.env
set +a

if [ "$IS_LOCAL" = "true" ]; then
    # update access for dashboard user
    psql -h localhost -p 5434 -U atlas_bpp_dashboard_user atlas_dev -c "update atlas_bpp_dashboard.registration_token set operating_city = '$DRIVER_CITY' where token = '0f3378e2-da5b-4eac-a0f6-397ca48358de';"
    psql -h localhost -p 5434 -U atlas_bpp_dashboard_user atlas_dev -c \
    "insert into atlas_bpp_dashboard.merchant_access (id, person_id, merchant_id, is2fa_enabled, merchant_short_id, operating_city, created_at) \
    VALUES ('fc0c37a1-69d5-7c19-b0fc-7692c8a1402f', '3680f4b5-dce4-4d03-aa8c-5405690e87bd', '94bbea0d-3c52-479b-81f5-eca4969ae797', 'false', 'NAMMA_YATRI_PARTNER', 'Bangalore', now()) ON CONFLICT DO NOTHING;"

    psql -h localhost -p 5434 -U atlas_driver_offer_bpp_user atlas_dev -c \
    "UPDATE atlas_driver_offer_bpp.document_verification_config \
        SET supported_vehicle_classes_json = (\
            SELECT jsonb_agg(\
                (element :: jsonb) || jsonb_build_object('bodyType', 'null')\
            )\
            FROM json_array_elements(document_verification_config.supported_vehicle_classes_json) AS element\
        )\
    WHERE vehicle_category = 'CAR' and document_type = 'VehicleRegistrationCertificate' and supported_vehicle_classes_json IS NOT NULL;"
fi

echo "Running driver locust ..."

# Run locust
locust -f driver.py --web-port 8100