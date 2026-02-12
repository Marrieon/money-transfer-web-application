# --- Phase 1 Models ---
from .user import User
from .wallet import Wallet
from .transaction import Transaction

# --- Phase 2 Models ---
from .savings_goal import SavingsGoal
from .audit_log import AuditLog

# --- Phase 3 Models ---
from .beneficiary import Beneficiary
from .money_circle import MoneyCircle
from .loan import Loan
from .notification import Notification

# --- Phase 4 Models (CORRECTED) ---
from .insurance import InsuranceProduct, UserInsurancePolicy
from .merchant import Merchant
from .trust_score import TrustScoreRecord