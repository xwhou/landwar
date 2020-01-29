#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-13 下午2:57
# @Author  : sgr
# @Site    : 
# @File    : action_result.py


class ActionResult:
    Success = {'code': 1, 'message': 'Success'}
    ErrorActionMsgType = {'code': 11, 'message': 'ErrorActionMsgType'}
    ErrorActionMsgParas = {'code': 12, 'message': 'ErrorActionMsgParas'}
    ErrorActionType = {'code': 13, 'message': 'ErrorActionType'}

    CantFindOperator = {'code': 21, 'message': 'CantFindOperator'}
    CantControlOnBoardOperator = {'code': 22, 'message': 'CantControlOnBoardOperator'}
    CantControlDiedOperator = {'code': 23, 'message': 'CantControlDiedOperator'}
    CantControlLostControlOperator = {'code': 24, 'message': 'CantControlLostControlOperator'}

    CantActionWhenGettingOn = {'code': 31, 'message': 'CantActionWhenGettingOn'}
    CantActionWhenGettingOff = {'code': 32, 'message': 'CantActionWhenGettingOff'}
    CantActionWhenChangingState = {'code': 33, 'message': 'CantActionWhenChangingState'}
    CantActionWhenStopping = {'code': 34, 'message': 'CantActionWhenStopping'}

    CantMoveCausePrepareJM = {"code": 40, "message": "CantMoveCausePrepareJM"}
    CantMoveCauseTooSteep = {'code': 41, 'message': 'CantMoveCauseTooSteep'}
    CantMoveUnderTireLv2 = {'code': 42, 'message': 'CantMoveUnderTireLv2'}
    CantCharge2UnderTireLv1 = {'code': 43, 'message': 'CantCharge2UnderTireLv1'}
    CantMoveKeptPeople = {'code': 44, 'message': 'CantMoveKeptPeople'}
    CantMarchCauseOperatorBlock = {'code': 45, 'message': 'CantMarchCauseOperatorBlock'}
    CantMarchNotCar = {'code': 46, 'message': 'CantMarchNotCar'}
    CantMarchOnNotRoad = {'code': 47, 'message': 'CantMarchOnNotRoad'}
    InvalidMovePath = {'code': 48, 'message': 'InvalidMovePath'}
    CantMarchToNotRoad = {'code': 49, 'message': 'CantMarchToNotRoad'}
    CantMoveWhenMoving = {'code': 490, 'message': 'CantMoveWhenMoving'}

    InvalidShootRole = {'code': 50, 'message': 'InvalidShootRole'}
    CantFindWeapon = {'code': 51, 'message': 'CantFindWeapon'}
    CantShootOfErrorObjectType = {'code': 52, 'message': 'CantShootOfErrorObjectType'}
    CantShootOfOutOfAim = {'code': 53, 'message': 'CantShootOfOutOfAim'}
    WeaponCooling = {'code': 54, 'message': 'WeaponCooling'}
    WeaponUnfolding = {'code': 55, 'message': 'WeaponUnfolding'}
    CantShootWhenMoving = {'code': 56, 'message': 'CantShootWhenMoving'}
    CantShootByKeptPeo = {'code': 57, 'message': 'CantShootByKeptPeo'}
    OperatorNotCarryThisWeapon = {'code': 58, 'message': 'OperatorNotCarryThisWeapon'}
    CantShootToFlyMissile = {'code': 59, 'message': 'CantShootToFlyMissile'}
    LackAmmunition = {'code': 60, 'message': 'LackAmmunition'}
    CantShootUnderMarch = {'code': 61, 'message': 'CantShootUnderMarch'}
    CantShootByUnLunchedFlyMissile = {'code': 62, 'message': 'CantShootByUnLunchedFlyMissile'}
    CantShootCauseCantSee = {'code': 63, 'message': 'CantShootCauseCantSee'}
    CantShootCauseInvalidAttackLevel = {'code': 64, 'message': 'CantShootCauseInvalidAttackLevel'}
    CantGuideCauseLackAbility = {'code': 70, 'message': 'CantGuideCauseLackAbility'}
    CantGuideCauseNotLaunched = {'code': 71, 'message': 'CantGuideCauseNotLaunched'}
    CantGuideCauseWeaponCooling = {'code': 72, 'message': 'CantGuideCauseWeaponCooling'}
    CantGuideCausePeoMoving = {'code': 73, 'message': 'CantGuideCausePeoMoving'}
    CantGuideCausePeoKept = {'code': 74, 'message': 'CantGuideCausePeoKept'}
    CantGuideCauseErrorLauncher = {'code': 75, 'message': 'CantGuideCauseErrorLauncher'}
    CantGuideCauseMoving = {'code': 76, 'message': 'CantGuideCauseMoving'}
    CantGuideCauseNotSee = {'code': 77, 'message': 'CantGuideCauseNotSee'}
    CantGuideCauseErrorWeapon = {'code': 78, 'message': 'CantGuideCauseErrorWeapon'}
    CantJMCauseNotArtillery = {'code': 80, 'message': 'CantJMCauseNotArtillery'}
    CantJMCauseWeaponCooling = {'code': 81, 'message': 'CantJMCauseWeaponCooling'}
    CantJMCauseWrongWeapon = {'code': 82, 'message': 'CantJMCauseWrongWeapon'}
    CantJMOutOfMap = {'code': 83, 'message': 'CantJMOutOfMap'}
    CantJMCauseWeaponUnfolding = {'code': 83, 'message': 'CantJMCauseWeaponUnfolding'}
    CantGetOnCauseWrongObjectType = {'code': 90, 'message': 'CantGetOnCauseWrongObjectType'}
    CantGetOnCausePeoKept = {'code': 91, 'message': 'CantGetOnCausePeoKept'}
    CantGetOnCauseDiffColor = {'code': 92, 'message': 'CantGetOnCauseDiffColor'}
    CantGetOnCauseTooFar = {'code': 93, 'message': 'CantGetOnCauseTooFar'}
    CantGetOnCauseCarKept = {'code': 94, 'message': 'CantGetOnCauseCarKept'}
    CantGetOnCauseMaxNum = {'code': 95, 'message': 'CantGetOnCauseMaxNum'}
    CantGetOnWhenMoving = {'code': 96, 'message': 'CantGetOnWhenMoving'}
    CantGetOffCauseCarKept = {'code': 100, 'message': 'CantGetOffCauseCarKept'}
    CantGetOffCauseNoPassengers = {'code': 101, 'message': 'CantGetOffCauseNoPassengers'}
    CantGetOffCauseAlreadyFlyMissile = {'code': 102, 'message': 'CantGetOffCauseAlreadyFlyMissile'}
    CantGetOffWhenMoving = {'code': 103, 'message': 'CantGetOffWhenMoving'}
    CantGetOffWhenGettingOff = {'code': 104, 'message': 'CantGetOffWhenGettingOff'}
    CantChangeStateCauseNotChange = {'code': 110, 'message': 'CantChangeStateCauseNotChange'}
    CantChangeStateCauseOnlyPeoCanCharge = {'code': 111, 'message': 'CantChangeStateCauseOnlyPeoCanCharge'}
    CantCharge1UnderTireLv2 = {'code': 112, 'message': 'CantCharge1UnderTireLv2'}
    CantSwitchStateWhenMoving = {'code': 113, 'message': 'CantSwitchStateWhenMoving'}
    CantHideForPlane = {'code': 114, 'message': 'CantHideForPlane'}
    CantOccupyCausePlane = {'code': 120, 'message': 'CantOccupyCausePlane'}
    CantOccupyCauseNotInCity = {'code': 121, 'message': 'CantOccupyCauseNotInCity'}
    CantOccupyCauseEnemyDefending = {'code': 122, 'message': 'CantOccupyCauseEnemyDefending'}
    CantOccupyCauseAlreadyMy = {'code': 123, 'message': 'CantOccupyCauseAlreadyMy'}
    CantRemoveKeepCauseNotPeo = {'code': 123, 'message': 'CantRemoveKeepCauseNotPeo'}
    CantRemoveKeepCauseNotKept = {'code': 124, 'message': 'CantRemoveKeepCauseNotKept'}
    CantRemoveKeepCauseLackBlood = {'code': 125, 'message': 'CantRemoveKeepCauseLackBlood'}


