"""
Management command to seed the database with realistic demo data
for development and testing.

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import Tenant, User
from assets.models import ProductType, Depot, Tank, PipelineSegment
from operations.models import Batch, VesselDischarge
from alerts.models import AlertRule


class Command(BaseCommand):
    help = 'Seed database with demo PipelineGuard data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding PipelineGuard demo data...')

        # ── Tenant ──
        tenant, _ = Tenant.objects.get_or_create(
            name='NNPC Retail',
            defaults={'domain_name': 'nnpc.pipelineguard.local',
                      'primary_color': '#0f172a', 'secondary_color': '#22c55e'}
        )
        self.stdout.write(f'  Tenant: {tenant.name} (API key: {tenant.api_key})')

        # ── Users ──
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@pipelineguard.local', 'role': 'SUPER_ADMIN',
                      'tenant': tenant, 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
        self.stdout.write(f'  Admin user: admin / admin')

        operator_user, created = User.objects.get_or_create(
            username='operator1',
            defaults={'email': 'operator@pipelineguard.local', 'role': 'OPERATOR',
                      'tenant': tenant},
        )
        if created:
            operator_user.set_password('operator1')
            operator_user.save()

        # ── Product Types ──
        products = {}
        product_data = [
            ('PMS', '#facc15', 0.74),   # Premium Motor Spirit (yellow)
            ('AGO', '#ef4444', 0.85),   # Automotive Gas Oil (red)
            ('DPK', '#a855f7', 0.80),   # Dual Purpose Kerosene (purple)
            ('JET A1', '#3b82f6', 0.80),  # Aviation fuel (blue)
        ]
        for name, color, sg in product_data:
            p, _ = ProductType.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={'color_code': color, 'specific_gravity': sg,
                          'max_interface_mixing_tolerance': 50.0},
            )
            products[name] = p

        # ── Depots ──
        depot_data = [
            ('Atlas Cove Terminal', 6.4280, 3.3970),
            ('Mosimi Depot', 6.6670, 3.5600),
            ('Satellite Depot Ejigbo', 6.5500, 3.3200),
            ('Ore Depot', 7.1000, 4.8700),
            ('Ibadan Depot', 7.3775, 3.9470),
        ]
        depots = {}
        for name, lat, lng in depot_data:
            d, _ = Depot.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={'latitude': lat, 'longitude': lng},
            )
            depots[name] = d

        # ── Tanks ──
        tank_configs = [
            ('Atlas Cove Terminal', [
                ('TK-101', 'PMS', 50000, 47000, 32000),
                ('TK-102', 'PMS', 50000, 47000, 41000),
                ('TK-201', 'AGO', 30000, 28000, 18000),
                ('TK-301', 'JET A1', 25000, 23000, 12000),
            ]),
            ('Mosimi Depot', [
                ('TK-401', 'PMS', 40000, 37000, 25000),
                ('TK-402', 'AGO', 30000, 28000, 22000),
                ('TK-501', 'DPK', 20000, 18000, 9000),
            ]),
            ('Satellite Depot Ejigbo', [
                ('TK-601', 'PMS', 35000, 33000, 29000),
                ('TK-602', 'AGO', 25000, 23000, 8000),
            ]),
        ]
        for depot_name, tanks in tank_configs:
            depot = depots[depot_name]
            for tank_name, prod, max_cap, safe_cap, vol in tanks:
                Tank.objects.get_or_create(
                    depot=depot, name=tank_name,
                    defaults={
                        'product_type': products[prod],
                        'max_capacity': max_cap,
                        'safe_fill_capacity': safe_cap,
                        'current_volume': vol,
                        'current_temperature': 32.5,
                        'status': 'ACTIVE',
                    },
                )

        # ── Pipeline Segments ──
        segment_data = [
            ('Atlas Cove – Mosimi (System 2B)', 'Atlas Cove Terminal', 'Mosimi Depot',
             65.0, 16, 12000, 'FLOWING', 850, 45),
            ('Mosimi – Ibadan', 'Mosimi Depot', 'Ibadan Depot',
             115.0, 12, 8000, 'FLOWING', 620, 38),
            ('Atlas Cove – Satellite', 'Atlas Cove Terminal', 'Satellite Depot Ejigbo',
             18.0, 10, 3500, 'STATIC', 0, 12),
            ('Mosimi – Ore', 'Mosimi Depot', 'Ore Depot',
             180.0, 14, 15000, 'MAINTENANCE', 0, 0),
        ]
        segments = {}
        for name, orig, dest, length, diam, vol, stat, flow, press in segment_data:
            seg, _ = PipelineSegment.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={
                    'origin': depots[orig], 'destination': depots[dest],
                    'length_km': length, 'diameter_inches': diam,
                    'volume_capacity': vol, 'status': stat,
                    'current_flow_rate': flow, 'current_pressure': press,
                    'geojson_path': {
                        'type': 'LineString',
                        'coordinates': [
                            [depots[orig].longitude, depots[orig].latitude],
                            [depots[dest].longitude, depots[dest].latitude],
                        ],
                    },
                },
            )
            segments[name] = seg

        # ── Batches ──
        now = timezone.now()
        batch_data = [
            ('BATCH-2026-001', 'Atlas Cove – Mosimi (System 2B)', 'PMS',
             'Atlas Cove Terminal', 'Mosimi Depot', 8000, 32.5, 'IN_TRANSIT'),
            ('BATCH-2026-002', 'Mosimi – Ibadan', 'AGO',
             'Mosimi Depot', 'Ibadan Depot', 5500, 45.0, 'IN_TRANSIT'),
            ('BATCH-2026-003', 'Atlas Cove – Mosimi (System 2B)', 'DPK',
             'Atlas Cove Terminal', 'Mosimi Depot', 3000, 0, 'SCHEDULED'),
        ]
        for bid, seg_name, prod, orig, dest, vol, pos, stat in batch_data:
            Batch.objects.get_or_create(
                batch_identifier=bid,
                defaults={
                    'segment': segments[seg_name],
                    'product_type': products[prod],
                    'origin_depot': depots[orig],
                    'destination_depot': depots[dest],
                    'total_volume': vol,
                    'current_position_km': pos,
                    'status': stat,
                    'start_time': now - timedelta(hours=6),
                    'estimated_arrival_time': now + timedelta(hours=8),
                },
            )

        # ── Vessel Discharge ──
        VesselDischarge.objects.get_or_create(
            tenant=tenant, vessel_name='MT Lagos Star',
            defaults={
                'terminal_depot': depots['Atlas Cove Terminal'],
                'product_type': products['PMS'],
                'total_volume': 45000,
                'discharged_volume': 28500,
                'status': 'DISCHARGING',
                'start_time': now - timedelta(hours=12),
                'estimated_completion_time': now + timedelta(hours=6),
            },
        )

        # ── Alert Rules ──
        alert_rules = [
            ('Low Ullage Warning', 'TANK', 'ullage', '<', 5000,
             'Tank {entity} ullage critically low: {value} bbl remaining'),
            ('Pipeline Offline Alert', 'PIPELINE', 'current_flow_rate', '==', 0,
             'Pipeline {entity} flow rate is zero — line may be offline'),
            ('High Interface Mixing', 'BATCH', 'current_position_km', '>', 60,
             'Batch {entity} position exceeded 60km: {value} km'),
        ]
        for name, etype, metric, cond, thresh, tmpl in alert_rules:
            AlertRule.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={
                    'entity_type': etype, 'metric': metric,
                    'condition': cond, 'threshold': thresh,
                    'message_template': tmpl, 'is_active': True,
                },
            )

        self.stdout.write(self.style.SUCCESS('✅ Demo data seeded successfully!'))
