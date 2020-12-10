from .errors import SkybrushStudioAddonError
from .model.formation import get_all_markers_from_formation
from .utils.identifiers import create_internal_id, is_internal_id

__all__ = (
    "create_transition_constraint_between",
    "find_transition_constraint_between",
    "is_transition_constraint",
)


def _get_id_for_formation_constraint(formation):
    # Make sure to update is_transition_constraint() as well if you change the
    # format of the ID
    return create_internal_id(f"To {formation.name}")


def create_transition_constraint_between(drone, formation):
    """Creates a transition constraint between the given drone and an arbitrary
    point of the formation.

    It is assumed that there is no such constraint between the drone and the
    formation yet, and that the formation is not empty.

    Returns:
        the constraint that was created
    """
    if not formation.objects:
        raise SkybrushStudioAddonError(
            "Cannot create constraint between a drone and an empty formation"
        )

    point = formation.objects[0]

    constraint = drone.constraints.new(type="COPY_LOCATION")
    constraint.name = _get_id_for_formation_constraint(formation)
    constraint.influence = 0
    constraint.target = point

    return constraint


def find_transition_constraint_between(drone, formation):
    """Finds the Blender "copy location" constraint object that exists between
    the given drone and any of the points in the given formation; the purpose
    of this constraint is to keep the drone at the location of the point in the
    formation and to drive it towards / away from it during transitions.

    Returns:
        the constraint or `None` if no such constraint exists
    """
    # Get all the points from the formation
    points = set(get_all_markers_from_formation(formation))

    for constraint in drone.constraints:
        if constraint.type != "COPY_LOCATION":
            continue

        if not is_internal_id(constraint.name):
            continue

        if constraint.target in points:
            return constraint

    return None


def is_transition_constraint(constraint):
    """Returns whether the given constraint object is a transition constraint,
    judging from its name and type.
    """
    return (
        constraint
        and getattr(constraint, "type", None) == "COPY_LOCATION"
        and is_internal_id(constraint.name)
        and "[To " in constraint.name
    )
