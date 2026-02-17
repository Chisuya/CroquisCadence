from dataclasses import dataclass
from typing import Literal, Optional, List

@dataclass
class SessionBlock:
    """
    Represents one segment of a drawing session.
    
    Examples:
    - 10 poses of 30 seconds each from "hands" folder
    - 5 minute break
    - 1 pose of 20 minutes from "full-body" and "poses" folders
    """
    
    # define fields
    block_type: Literal["pose", "break"]
    duration: int
    count: int
    # defaults to none
    folder_paths: Optional[List[str]] = None
    interval_pings: Optional[List[int]] = None
    nsfw_filter: str = "all"  # "all", "sfw", or "nsfw"
    
    def __post_init__(self):
        """Validation after initialization"""

        # Validation checks:
        # validate block_type
        if self.block_type not in ["pose", "break"]:
            raise ValueError(f"Invalid block_type: {self.block_type}. Must be'pose' or 'break'")
        
        # validate duration
        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
        
        # validate count
        if self.count <= 0:
            raise ValueError(f"Count must be positive, got {self.count}")
        
        # validate interval_pings (only if provided)
        if self.interval_pings is not None:
            for ping_time in self.interval_pings:
                if ping_time <= 0:
                    raise ValueError(
                        f"Interval ping times must be positive, got {ping_time}"
                    )
                if ping_time >= self.duration:
                    raise ValueError(
                        f"Interval ping {ping_time}s must be less than duration {self.duration}s"
                    )

        # validate breaks don't have folder paths
        if self.block_type == "break" and self.folder_paths is not None:
            # Allow poses to have none bc it means "all folders", ImageCollection will handle None
            raise ValueError("Break blocks cannot have folder_paths")
    
    def total_duration(self) -> int:
        """Calculate total time for this block in seconds"""
        return self.count * self.duration

@dataclass
class Session:
    """A complete drawing session w/ multiple blocks"""
    name: str
    blocks: List[SessionBlock]
    
    def total_duration(self) -> int:
        """Calculate total session time in seconds"""
        duration = 0
        for block in self.blocks:
            duration += block.total_duration()
        return duration

    def format_duration(self) -> str:
        """Return human-readable duration ex: 1h 55m"""
        total_seconds = self.total_duration()
        hours, remaining = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        parts = [
            f"{hours}h" if hours else None,
            f"{minutes}m" if minutes else None,
            f"{seconds}s" if seconds else None
        ]
        result = " ".join(filter(None, parts))
        return result if result else "0s"